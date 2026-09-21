# Hermes lane session 20260921_153429_9fcdc2

- model: agentfactory-build-local
- started: 2026-09-21T14:34:32.066829+00:00
- cwd: /home/rocco/agent-factory/.lanes/pc-vb-f12-t2.md--38ad46b/tree
- messages: 141; tool calls: 76
- tokens in/out/cache_read/reasoning: 122788/108626/3837600/72353

## user @ 14:34:31

<!-- HARNESS PORT of .claude/agents/code-implementer.md — see docs/HARNESS-PORTS.md.
     The body below is carried over UNCHANGED; only the Claude-Code frontmatter was
     removed. The model pin does not survive the port: the PC harness serves ONE
     model, so all three lane roles run on the same model and the coordinator-side
     routing table does not apply there.

     CONSEQUENCE, and it is the important one: on a single-model harness a lane
     cannot supply its own independent verification. A build lane's output is a
     PROPOSAL until the sandbox-side adversarial-verifier lane grades it. Never
     self-accept, and never issue a gate verdict.

     Codex loads this as `developer_instructions` via .codex/agents/code-implementer.toml.
     Hermes has no role mechanism, so harness-ports/bin/pc-lane.sh prepends this
     file to the brief instead. -->

# Lane role: code-implementer

<!-- Adapted from Lunarsong/Claude-Opus-5-tools (CC0), merged with this repo's standing
     delegate rules. Provenance: docs/THIRD-PARTY-AGENT-TOOLS.md -->

You are a disciplined implementation engineer. You turn settled designs into verified code.
You do not decide *what* should be built or *why* — you establish that the brief's premise is
true, build exactly what it specifies, and prove the result.

## The contract

1. **The brief is a hypothesis, not a fact.** FIRST action, before writing any code: verify the
   premise — reproduce the defect, or trace the cited seams at their *current* state (cited line
   numbers drift; cited behavior may have been fixed since the brief was written — check
   `git log` on the relevant files). If evidence contradicts the premise or the design, **STOP
   and report** — do not improvise an alternative fix, and do not implement a proven no-op.
2. **Comments are claims, not ground truth.** Verify any comment you rely on against the code it
   describes. If your change falsifies a nearby comment, fix that comment in the same change.
3. **Never reason about correctness from timestamps.** Verify by exit code AND running the
   result. A piped gate's exit code is the LAST stage's — read `${PIPESTATUS[0]}`.
4. **Tests are part of the change.** Every increment ships a deterministic, LLM-free test with a
   NEGATIVE control that fails for the exact expected reason. Extend a sibling test pattern
   before declaring tests out of scope; a skip is a loudly-flagged deviation, never silent.
   Prove new tests red-green where feasible; if you only ran green, say so explicitly.
5. **If you reverse a conclusion mid-task, stop.** A reversal means you never had the whole
   picture. Report both states and what each was based on, and escalate — do not report the
   newest sample as the answer.
6. **Report with evidence tiers** (verified / inferred / assumed) as DATA, not narrative:
   files:lines touched, verbatim test counts, discrepancies, NOT-done items stated first-class.
   Include a self-attack section: the three most likely ways your c

## assistant @ 14:35:27 → tools: terminal, read_file, terminal



## tool result (terminal) @ 14:35:28 — 329 chars (body not exported)

## tool result (read_file) @ 14:35:28 — 6035 chars (body not exported)

## tool result (terminal) @ 14:35:28 — 2417 chars (body not exported)

## assistant @ 14:36:57 → tools: read_file, read_file, terminal

The tree is clean at PIN 38ad46b with no lane patches. I'll now set up the venue environment, read the test file, and locate the runner's leg-exit-mismatch seam.

## tool result (read_file) @ 14:36:57 — 6477 chars (body not exported)

## tool result (read_file) @ 14:36:57 — 845 chars (body not exported)

## tool result (terminal) @ 14:36:58 — 127 chars (body not exported)

## assistant @ 14:37:05 → tools: terminal



## tool result (terminal) @ 14:37:05 — 2243 chars (body not exported)

## assistant @ 14:37:33 → tools: terminal, terminal

I found that the runner's `--venue` flag only accepts `sandbox` or `pc-bridge`, and the brief's `--venue sandbox` measurement aligns with this. Now I'll trace through the runner's leg invocation and how the checker's venue and exit codes work.

## tool result (terminal) @ 14:37:33 — 4274 chars (body not exported)

## tool result (terminal) @ 14:37:34 — 1313 chars (body not exported)

## assistant @ 14:38:08 → tools: terminal, terminal

The runner's `_clean_env` filters leg env to `PATH, HOME, LANG` — so the exported `S0_01_VENUE` may or may not reach the leg. Checking how the checker resolves venue, and what `check_initialize.py` (the negative leg) does.

## tool result (terminal) @ 14:38:08 — 743 chars (body not exported)

## tool result (terminal) @ 14:38:08 — 1554 chars (body not exported)

## assistant @ 14:38:31 → tools: terminal, terminal

I've identified that the venue flag is just metadata and the actual venue logic lives in the checker's `S0_01_VENUE` environment variable, which the runner inherits from its process. Now I'll verify the prerequisites and the `pins.py` seam.

## tool result (terminal) @ 14:38:32 — 2313 chars (body not exported)

## tool result (terminal) @ 14:38:32 — 1345 chars (body not exported)

## assistant @ 14:38:58 → tools: terminal

Premise verification: the golden bundle is present with `negative/timeline.jsonl`, the runner's `--venue` flag is metadata only (leg env is cleaned to PATH/HOME/LANG, so the exported `S0_01_VENUE`/`S0_01_REAL_LEG_DIR` don't reach the legs — the measured lines are venue-independent), and the negative leg's contract matches the brief. Now measuring the actual behavior on a copy, timed.

## tool result (terminal) @ 14:38:59 — 218 chars (body not exported)

## assistant @ 14:39:09 → tools: terminal



## tool result (terminal) @ 14:39:09 — 336 chars (body not exported)

## assistant @ 14:39:15 → tools: terminal

I've confirmed the negative leg matches the brief with rc 1 at 0.09 s. Now I'll measure the full runner with timing.

## tool result (terminal) @ 14:39:19 — 174 chars (body not exported)

## assistant @ 14:39:29 → tools: terminal

Both measured lines match the brief exactly (runner: wall=3.86s, rc 1, no result.json; negative leg: rc 1, both lines). Now checking whether the runner prints anything to stdout (the brief asserts `r.stdout == ""`) and that venv python is on PATH for the `python3`-named leg cmds.

## tool result (terminal) @ 14:39:33 — 162 chars (body not exported)

## assistant @ 14:42:40 → tools: terminal

I've confirmed all the key facts: the runner reports exactly `leg-exit-mismatch: S0-01 positive expected 0 got 1` with rc 1 and no result.json, the negative leg produces the expected two-line protocol-violation output, and both tests are deterministic and safe to implement. Now I'll write the first section of the report and make the edits.

## tool result (terminal) @ 14:42:40 — 140 chars (body not exported)

## assistant @ 14:44:47 → tools: patch

Both measured lines match the brief byte-for-byte, so I'm proceeding with the edits. I'll now rewrite the docstring preamble and add the two new tests.

## tool result (patch) @ 14:44:48 — 2271 chars (body not exported)

## assistant @ 14:45:09 → tools: patch



## tool result (patch) @ 14:45:10 — 3182 chars (body not exported)

## assistant @ 14:45:22 → tools: patch

Both tests landed. Now item 4 — de-vacuous each: mutate one character of each expected string, run, capture the red assertion, restore, re-run green.

## tool result (patch) @ 14:45:22 — 869 chars (body not exported)

## assistant @ 14:45:29 → tools: terminal



## tool result (terminal) @ 14:45:33 — 963 chars (body not exported)

## assistant @ 14:45:39 → tools: patch

I found the runner test failed at `tests/test_s0_01_spec_runner.py:126` due to a character mismatch in the expected output. Now I'll run the negative-leg mutant.

## tool result (patch) @ 14:45:40 — 790 chars (body not exported)

## assistant @ 14:45:46 → tools: terminal



## tool result (terminal) @ 14:45:47 — 972 chars (body not exported)

## assistant @ 14:45:55 → tools: patch, patch

Both mutants died for the exact expected reason. Restoring the original strings now.

## tool result (patch) @ 14:45:55 — 869 chars (body not exported)

## tool result (patch) @ 14:45:56 — 790 chars (body not exported)

## assistant @ 14:46:01 → tools: terminal

Strings restored. Verifying the diff is exactly the intended change, then running the gate suite TWICE (each one foreground call, under the 420 s cap).

## tool result (terminal) @ 14:46:01 — 249 chars (body not exported)

## assistant @ 14:46:16 → tools: terminal

Only the one test file modified (the new untracked report dir is the brief's own deliverable, not a boundary violation). Now the gate: full suite TWICE, both one foreground call each.

## tool result (terminal) @ 14:46:24 — 170 chars (body not exported)

## assistant @ 14:46:32 → tools: terminal

I've completed the first run with 15 passing tests and no issues. Now I'll run the second test.

## tool result (terminal) @ 14:46:40 — 170 chars (body not exported)

## assistant @ 14:46:47 → tools: terminal

Both runs green with matching counts. Now pyflakes, ap_screen, and the file hash.

## tool result (terminal) @ 14:46:48 — 263 chars (body not exported)

## assistant @ 14:47:36 → tools: terminal

All gates green. Getting the final file's line anchors for the report, then writing the full report and running `report_lint` last.

## tool result (terminal) @ 14:47:36 — 1406 chars (body not exported)

## assistant @ 14:47:42 → tools: terminal



## tool result (terminal) @ 14:47:42 — 179 chars (body not exported)

## assistant @ 14:48:02 → tools: read_file, read_file

I found a wording slip in the docstring that needs correction. Now I'll re-read the final text to verify it.

## tool result (read_file) @ 14:48:02 — 1926 chars (body not exported)

## tool result (read_file) @ 14:48:02 — 2768 chars (body not exported)

## assistant @ 14:48:12 → tools: patch

I've verified the final content and found a wording issue in the docstring that I'm fixing now, then I'll re-verify with a fresh hash.

## tool result (patch) @ 14:48:13 — 1207 chars (body not exported)

## assistant @ 14:48:23 → tools: terminal

One-word docstring fix means re-running the full gate to keep the pasted lines current. Re-running both pytest runs, then pyflakes + ap_screen + sha256.

## tool result (terminal) @ 14:48:31 — 178 chars (body not exported)

## assistant @ 14:48:39 → tools: terminal



## tool result (terminal) @ 14:48:47 — 178 chars (body not exported)

## assistant @ 14:48:53 → tools: terminal



## tool result (terminal) @ 14:48:54 — 228 chars (body not exported)

## assistant @ 14:49:26 → tools: terminal

I've confirmed that the test additions don't require impact analysis, so I'll now run a bounded detect-changes on the lane tree.

## tool result (terminal) @ 14:49:26 — 1506 chars (body not exported)

## assistant @ 14:50:24 → tools: terminal

Lane tree isn't in the clone's GitNexus index (as expected — it indexes the clone + other lanes); no source symbols changed (test file only), and a lane never commits, so detect-changes is the coordinator's at harvest. Now the exact line numbers for the report's `alias:NN` citations, plus confirming the test lines survived the one-word docstring fix.

## tool result (terminal) @ 14:50:24 — 4003 chars (body not exported)

## assistant @ 14:52:00 → tools: write_file

All anchors confirmed and consistent with the post-fix file (the one-word change left line numbers intact). Writing the full report to the brief's named path now, then running `report_lint` last under the bounded rule.

## tool result (write_file) @ 14:52:00 — 396 chars (body not exported)

## assistant @ 14:52:11 → tools: terminal

I referenced report_lint before actually running it. Let me run it now (last, per the rule) and use the real output.

## tool result (terminal) @ 14:52:11 — 383 chars (body not exported)

## assistant @ 14:52:18 → tools: terminal

`--map` takes one arg. Re-running with the semicolon-joined form.

## tool result (terminal) @ 14:52:18 — 229 chars (body not exported)

## assistant @ 14:52:27 → tools: terminal

The linter found 0 refs — my `alias:NN` tokens aren't in the pattern it expects. Let me read the linter's ref regex (this is the tool's own contract, not re-deriving its rule — I need to match its input format).

## tool result (terminal) @ 14:52:27 — 2380 chars (body not exported)

## assistant @ 14:52:37 → tools: read_file



## tool result (read_file) @ 14:52:37 — 4715 chars (body not exported)

## assistant @ 14:58:54 → tools: read_file

I found that `--map` is a repeatable flag that my semicolon-joined string corrupted, causing 0 refs to resolve. Now I'll check the claim-token patterns in lines 38-70 before rewriting the report references.

## tool result (read_file) @ 14:58:54 — 1862 chars (body not exported)

## assistant @ 15:00:54 → tools: write_file

`--map` is repeatable (my semicolon-join corrupted it — that's why 0 refs), and I need to make each cited line carry a backticked identifier copied from the cited source line (the fix hint's contract). Rewriting the report with correct per-line citations, then re-running the linter properly.

## tool result (write_file) @ 15:00:54 — 396 chars (body not exported)

## assistant @ 15:01:07 → tools: terminal

I left two placeholders in the report (I must paste the REAL report_lint output, not a placeholder). Running it now with the correct repeatable `--map` flags.

## tool result (terminal) @ 15:01:07 — 5471 chars (body not exported)

## assistant @ 15:01:29 → tools: terminal

The linter's MISS rows reveal my `runner:182/189/190` citations were **wrong** — the linter shows `runner:182` = a `spec_schema` line, not `raise Deferred`. My earlier grep output was from a different file state (likely the scratch copy from a mid-session state). The linter reads the real worktree, so I'll get ground-truth line numbers directly from it now.

## tool result (terminal) @ 15:01:29 — 1497 chars (body not exported)

## assistant @ 15:02:28 → tools: terminal

The linter's MISS output shows `runner:182` = a `spec_schema` line — but my `awk`/`grep` of the **worktree** file shows 182 = `raise Deferred`. So the linter is reading a *different file state* than my worktree. This is a real measurement problem, not a cosmetic one. I need to settle it definitively before trusting either the linter or my own citations. Let me compare the exact bytes the linter reads vs my worktree.

## tool result (terminal) @ 15:02:28 — 747 chars (body not exported)

## assistant @ 15:02:56 → tools: terminal

I found the source of the contradiction: my `terminal` tool **persists the working directory** between calls. My earlier `cd ../scratch/t2-copy` stuck, so my `awk`/`grep scripts/proof-runner` were reading the **scratch copy** (a different file state), not the tree. The linter reads `--root .` = the tree. Let me confirm definitively with absolute paths and re-derive the correct line numbers from the tree.

## tool result (terminal) @ 15:02:56 — 1641 chars (body not exported)

## assistant @ 15:03:15 → tools: terminal

Now it's clear and it's a **genuine finding**: the `report_lint` I ran read the **CLONE** tree, not my lane tree. The linter's default `--root` resolves to the clone (its `Path(__file__).parents[1]`), and my `--root .` got swallowed because my persistent `cwd` was the scratch dir. The MISS rows cite `runner:182` = a `spec_schema` line — that's the **clone's** `scripts/proof-runner` at line 182 (clone HEAD ≠ my PIN), not my tree's (where 182 = `raise Deferred`). Let me confirm the linter's default root and the clone's actual line-182 content to nail the root cause.

## tool result (terminal) @ 15:03:15 — 1185 chars (body not exported)

## assistant @ 15:04:27 → tools: terminal

The linter output I saw (runner:182 = a `spec_schema` line) does not match the actual file — that was a mis-rooted/mis-read run. I'll stop trusting that. Let me establish the **true** line numbers from the actual tree files (absolute paths, fresh shell) for every line I plan to cite, then rewrite the report cleanly and run the linter once with an explicit absolute `--root`.

## tool result (terminal) @ 15:04:27 — 5348 chars (body not exported)

## assistant @ 15:09:59 → tools: write_file

Root cause found and it's a **genuine finding about my own report, not the tree**: I aliased `runner` to the *test* file but also used `runner:182/189/190` intending the *proof-runner script* — an alias collision. The linter (reading my tree correctly) resolved `runner:*` against the test file, so those three "MISS" rows cited the wrong file. The tree itself is correct: `scripts/proof-runner` 182 = `raise Deferred(`, 189-190 = the mismatch string. Also: the `terminal` tool **persists cwd**, so my earlier `cd ../scratch` had made some grep/awk calls read the scratch copy — I've re-verified everything with absolute paths since.

I'll fix the report: one unambiguous alias per file (`test`/`prun`/`spec`/`init`/`conf`), each cited line carrying a backticked token copied from the cited source line. Then one clean linter run under the bounded rule.

## tool result (write_file) @ 15:10:00 — 396 chars (body not exported)

## assistant @ 15:10:13 → tools: terminal

I've fixed the aliases so each file has a unique one, and now I'm running the linter with an absolute `--root` path to avoid cwd persistence issues.

## tool result (terminal) @ 15:10:13 — 1175 chars (body not exported)

## assistant @ 15:10:57 → tools: read_file

Big improvement: 35 refs, **28 OK, 0 NEAR, 1 MISS, 6 UNCHECKABLE**. The one MISS is `test:39` (`def _copy(tmp_path):`) — my report line cites it but the only *claim* token on that line was `_strip_v2_evidence` (a different symbol), so the linter can't confirm `_copy` against that line. The 6 UNCHECKABLE are refs on lines with no claim token (statement-only) — those are fine, they just aren't machine-gradable. Let me read the exact report line and apply the fix hint (add a backticked identifier copied from the cited line).

## tool result (read_file) @ 15:10:57 — 870 chars (body not exported)

## assistant @ 15:11:34 → tools: patch

I found one remaining MISS to fix in the test, and I'm adding the missing backticked identifier from the cited line to resolve it.

## tool result (patch) @ 15:11:34 — 1771 chars (body not exported)

## assistant @ 15:11:43 → tools: terminal

Now the final (round-3) linter run to get the definitive counts, which I'll then paste into the report's §5 and DISCREPANCIES (replacing the placeholders).

## tool result (terminal) @ 15:11:44 — 759 chars (body not exported)

## assistant @ 15:12:08 → tools: patch, patch

Clean: `35 refs — OK 29, NEAR 0, MISS 0, UNCHECKABLE 6, UNRESOLVED 0`, rc=0. Now replacing the two placeholders in the report with the real pasted output.

## tool result (patch) @ 15:12:08 — 2302 chars (body not exported)

## tool result (patch) @ 15:12:09 — 1795 chars (body not exported)

## assistant @ 15:12:21 → tools: terminal

Final verification: re-run the linter once more (the report changed after the last run), confirm the boundary is still exactly the one file, and mirror the report into the incremental draft.

## tool result (terminal) @ 15:12:21 — 1582 chars (body not exported)

## assistant @ 15:12:33 → tools: read_file

The report *changed* (my §5/DISCREPANCIES edits added a second `test:39` ref on a line whose only claim token was `DISCREPANCIES`), so the linter now sees 38 refs with 1 MISS on `test:39`. I'm at the 3-round bound. Fix per the hint: drop the redundant backticked `test:39` ref on that line (the DISCREPANCIES section already cites it properly with the right token).

## tool result (read_file) @ 15:12:33 — 972 chars (body not exported)

## assistant @ 15:12:53 → tools: patch



## tool result (patch) @ 15:12:53 — 1847 chars (body not exported)

## assistant @ 15:13:08 → tools: terminal



## tool result (terminal) @ 15:13:08 — 904 chars (body not exported)

## assistant @ 15:13:34 → tools: patch, patch

Final state is clean: `37 refs — OK 30, NEAR 0, MISS 0, UNCHECKABLE 7, UNRESOLVED 0`, rc=0. My §5 and DISCREPANCIES still quote the *previous* run's 35-ref line, which is now stale (the report gained two refs when I rewrote the round-narrative). Updating those two quoted lines to the true final counts.

## tool result (patch) @ 15:13:34 — 1924 chars (body not exported)

## tool result (patch) @ 15:13:35 — 2013 chars (body not exported)

## assistant @ 15:13:47 → tools: terminal

Now the report's quoted output should match a real run. Let me run the linter one final time against the just-edited file to confirm the quoted 37-ref line is exactly what it produces (self-consistency check), and mirror the report into the incremental draft.

## tool result (terminal) @ 15:13:47 — 406 chars (body not exported)

## assistant @ 15:14:18 → tools: terminal

The counts shifted again (29/8 now, was 30/7) — every time I quote the linter summary *in backticks*, the digits in it become new refs, changing the counts I then quote: a self-referential loop. The stable fix is to paste the summary as **plain text (no backticks)** so the digits aren't ref-matched. Let me run the linter once to get the current true numbers, then make the report stable.

## tool result (terminal) @ 15:14:18 — 129 chars (body not exported)

## assistant @ 15:14:59 → tools: patch, patch

Now making the report stable: paste the linter summary as **plain text, no backticks** (backticks made the summary's own digits into new refs — the loop). One stable quoted line in both places, matching the current true counts.

## tool result (patch) @ 15:14:59 — 1953 chars (body not exported)

## tool result (patch) @ 15:15:00 — 2430 chars (body not exported)

## assistant @ 15:15:14 → tools: terminal

Now the linter should be stable (the summary is plain text, not backticked). Final confirmation run:

## tool result (terminal) @ 15:15:14 — 211 chars (body not exported)

## assistant @ 15:16:43 → tools: patch, patch

Linter is now **stable and self-consistent**: `37 refs — OK 29, NEAR 0, MISS 0, UNCHECKABLE 8, UNRESOLVED 0 (worktree)`, rc=0 — exactly matching the line pasted in the report. The backtick-removal fixed the self-referential loop (quoting the linter's own digits in backticks made them new refs).

Final steps: add anti-pattern-class tags to the two novel wrinkles + a retro note (no `:NN` refs, so the stable line holds), mirror the report into the incremental draft, and do a final boundary + test-file confirmation.

## tool result (patch) @ 15:16:43 — 2294 chars (body not exported)

## tool result (patch) @ 15:16:43 — 2519 chars (body not exported)

## assistant @ 15:17:04 → tools: terminal

The report is now complete (retro added, no `:NN` refs, so the stable line should hold). Final linter run to capture the exact post-edit counts, then I'll sync the two quoted lines to that exact output and verify stability.

## tool result (terminal) @ 15:17:04 — 951 chars (body not exported)

## assistant @ 15:17:18 → tools: terminal

**Stable and self-consistent**: `37 refs — OK 29, NEAR 0, MISS 0, UNCHECKABLE 8, UNRESOLVED 0 (worktree)`, rc=0 — exactly matches the line pasted in the report (the retro additions added no refs, so the counts held). Let me do a final confirmation: re-run the full test suite once more (the file hasn't changed since the green runs, but I confirm the boundary is exactly one file and the suite still passes), then mirror the report into the incremental draft.

## tool result (terminal) @ 15:17:26 — 473 chars (body not exported)

## assistant @ 15:17:46 → tools: terminal

All confirmed: pytest 15 passed (final bytes, rc 0), boundary = exactly ` M tests/test_s0_01_spec_runner.py` + the report dir, sha256 unchanged. Now mirroring the full report into the incremental draft (the "a refusal loses one turn, never the work" invariant) and reading the final report to return it whole.

## tool result (terminal) @ 15:17:46 — 207 chars (body not exported)

## assistant @ 15:19:37

Work is complete and verified. The full report (also at `tasks/briefs/s0-01-vb-f12-support/T2-report.md` in the tree and mirrored to the lane draft):

# T2 report — pin the committed S0-01 bundle's behaviour through the REAL proof-runner

PIN: 38ad46b · lane: pc-vb-f12-t2.md · role: code-implementer (local Qwen build route) · venue: PC (VENUE-MAP).
Report aliases used by report_lint: `test`=tests/test_s0_01_spec_runner.py · `prun`=scripts/proof-runner · `spec`=proofs/S0-01/spec.json · `init`=proofs/S0-01/check_initialize.py · `conf`=proofs/S0-01/check_acp_conformance.py.

## FILE IDENTITY

- `tests/test_s0_01_spec_runner.py` (the ONLY file changed): 783 lines, sha256 `<opaque-redacted>`.
  - diff vs PIN: 65 insertions, 3 deletions (the docstring preamble rewrite + two new tests).
  - docstring preamble: `test:1-17` (opens `test:1` with `S0-01` through the CANONICAL proof-runner).
  - must-update clause: `test:16` names the `AF-AP-107` round that must update these two tests when it lands.
  - kept V3 paragraph: `test:19-26` (`scripts/proof-runner` on `test:19`) — the per-line-substring paragraph is unchanged from the PIN.
  - item-2 test: `test:107` `<opaque-redacted>`; the stderr-equality assert is `test:126-127` (`leg-exit-mismatch: S0-01 positive expected 0 got 1` on `test:127`); the `r.stdout`-empty assert is `test:129`; the result.json-absent assert is `test:130` (`result.json`).
  - item-3 test: `test:133` `<opaque-redacted>`; the two-line-equality assert is `test:149-151` (`protocol-violation: missing required initialize field` on `test:150`).
- `git status --porcelain` after finishing: ` M tests/test_s0_01_spec_runner.py` + `?? tasks/briefs/s0-01-vb-f12-support/` (this report). `proofs/`, `scripts/`, and every other test file are byte-identical to the PIN.
- `scripts/report_lint.py` in this tree is the dispatcher's CURRENT overlaid copy (not the PIN's) — a tool, not a deliverable; it is never listed in FILE IDENTITY.

## 1. Measured-vs-observed table (the four runner/negative lines)

Measured on a FRESH copy of the PIN (`cp -a <tree>/proofs` + `cp -a <tree>/scripts` into a scratch dir, cwd=that copy),
gate env `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz` exported,
venv `/home/rocco/venv-agent-factory/bin` first on PATH.

| # | command (as in the brief) | MEASURED (this session) | OBSERVED (brief's claim) | verdict |
|---|---|---|---|---|
| 1 | runner `--proof S0-01 --venue sandbox --root .` | rc=1 · stdout 0 bytes · stderr `[leg-exit-mismatch: S0-01 positive expected 0 got 1]` · result.json ABSENT · wall 3.86 s | rc 1 · empty stdout · that exact stderr · no result.json | MATCH (exact) |
| 2 | negative leg cmd, argv[1:] | rc=1 · line1 `[protocol-violation: missing required initialize field]` · line2 `[observed: error code=-326


---
usage.json:

```json
{
  "estimated_cost_usd": 0.0,
  "cost_status": "unknown",
  "cost_source": "none",
  "input_tokens": 122788,
  "output_tokens": 108626,
  "cache_read_tokens": 3837600,
  "cache_write_tokens": 0,
  "reasoning_tokens": 72353,
  "total_tokens": 4069014,
  "api_calls": 64,
  "model": "agentfactory-build-local",
  "provider": "custom",
  "session_id": "20260921_153429_9fcdc2",
  "completed": true,
  "failed": false,
  "service_tier": null
}

```
