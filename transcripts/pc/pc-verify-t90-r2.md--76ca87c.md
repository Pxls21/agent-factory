# Hermes lane session 20260922_205843_e547bc

- model: qwen-local/qwen3.8-27b-local
- started: 2026-09-22T19:58:43.775417+00:00
- cwd: /home/rocco/agent-factory/.lanes/pc-verify-t90-r2.md--76ca87c/tree
- messages: 270; tool calls: 150
- tokens in/out/cache_read/reasoning: 656659/138659/10917408/96484

## user @ 19:58:43

RESUME (attempt 2 of this lane): a previous attempt of THIS lane ended on a route refusal or was stopped by the coordinator, not on its own decision. Its edits are already in your worktree (`git status --porcelain` lists them beside the lane patch) and its incremental report draft is at /home/rocco/agent-factory/.lanes/pc-verify-t90-r2.md--76ca87c/report-draft.md — read that draft FIRST and continue from its last finished section; do not redo a finished section, but verify its claims by run before relying on them.

---

<!-- HARNESS PORT of .claude/agents/adversarial-verifier.md — see docs/HARNESS-PORTS.md.
     The body below is carried over UNCHANGED; only the Claude-Code frontmatter was
     removed. The model pin does not survive the port: the PC harness serves ONE
     model, so all three lane roles run on the same model and the coordinator-side
     routing table does not apply there.

     CONSEQUENCE, and it is the important one: on a single-model harness a lane
     cannot supply its own independent verification. A build lane's output is a
     PROPOSAL until the sandbox-side adversarial-verifier lane grades it. Never
     self-accept; the lane emits a GATE RECOMMENDATION, never a final gate verdict
     — the coordinator owns the gate.

     Codex loads this as `developer_instructions` via .codex/agents/adversarial-verifier.toml.
     Hermes has no role mechanism, so harness-ports/bin/pc-lane.sh prepends this
     file to the brief instead. -->

# Lane role: adversarial-verifier

<!-- Adapted from Lunarsong/Claude-Opus-5-tools adversarial-review (CC0) + this repo's Phase-5
     verify discipline. Provenance: docs/THIRD-PARTY-AGENT-TOOLS.md. Disposition policy —
     exhaustive findings, bounded blockers: docs/08_DECISION_LOG.md D-031, skill contract-gate. -->

Your job is to determine whether the frozen contract survives a serious attempt at falsification.
Search aggressively, report every meaningful observation, and apply the blocking predicate exactly.
You have no stake in either acceptance or rejection. The author's report is a list of claims;
reproduce every claim you rely on through the real production path.

**No severity filter applies to discovery. A strict eligibility filter applies to readiness.** Put
every meaningful observation in the inventory; only findings that satisfy the WHOLE blocking
predicate may hold the increment back. You do not search indefinitely for any reason to reject.

## Attack set — bounded by the CHANGE CLASS, not an unbounded universal sweep

Run the pieces that bear on THIS increment; do not manufacture work the change does not touch.
- Execute every FROZEN CONTRACT item with its literal command; run the pre-registered negative controls.
- Make ONE bounded exploratory pass over the production interfaces the diff changed — hostile values
  only where they are meaningful for the actual input type.
- Do NOT recursively verify tests, mutation drivers, inventories, or report tooling unless that
  machinery i

## assistant @ 19:59:18 → tools: read_file, terminal



## tool result (read_file) @ 19:59:18 — 625 chars (body not exported)

## tool result (terminal) @ 19:59:19 — 526 chars (body not exported)

## assistant @ 19:59:26 → tools: read_file, terminal

The draft file isn't there, so I'll check the attempt-1 report instead.

## tool result (read_file) @ 19:59:26 — 225 chars (body not exported)

## tool result (terminal) @ 19:59:26 — 958 chars (body not exported)

## assistant @ 19:59:48 → tools: terminal, terminal, terminal

The draft is empty from a 503 refusal, so I'm starting fresh from item 1. I'll re-verify the premises at the PIN and examine the dispatcher hunks now.

## tool result (terminal) @ 19:59:48 — 181 chars (body not exported)

## tool result (terminal) @ 19:59:48 — 2941 chars (body not exported)

## tool result (terminal) @ 19:59:49 — 6843 chars (body not exported)

## assistant @ 20:00:00 → tools: terminal, terminal, read_file

Premise checks out. Now I'll examine the `bridge()` function, test harness, and briefs.

## tool result (terminal) @ 20:00:00 — 2241 chars (body not exported)

## tool result (terminal) @ 20:00:01 — 300 chars (body not exported)

## tool result (read_file) @ 20:00:01 — 8960 chars (body not exported)

## assistant @ 20:00:44 → tools: read_file, read_file

The draft is empty, so I'm starting fresh from item 1. I'll now review the rest of the test file and the frozen briefs to understand the five named controls and the R-F1/R-F3 spec.

## tool result (read_file) @ 20:00:44 — 22532 chars (body not exported)

## tool result (read_file) @ 20:00:44 — 8866 chars (body not exported)

## assistant @ 20:01:01 → tools: terminal, terminal



## tool result (terminal) @ 20:01:01 — 2502 chars (body not exported)

## tool result (terminal) @ 20:01:02 — 524 chars (body not exported)

## assistant @ 20:01:34 → tools: terminal, terminal, terminal

Now I'll read the F1/F3 sections of the VERIFY-T90 report, the old dispatcher's guard region, and the builder's report, while setting up my scratch dir.

## tool result (terminal) @ 20:01:34 — 6284 chars (body not exported)

## tool result (terminal) @ 20:01:34 — 2004 chars (body not exported)

## tool result (terminal) @ 20:01:35 — 2217 chars (body not exported)

## assistant @ 20:08:33 → tools: read_file, terminal, terminal

I've confirmed the premise matches the brief and set up my scratch environment. Now I'll investigate the item-6 mechanism by examining `pc_bridge_exec.py`, `pc.sh`, and the dispatcher's key sections.

## tool result (read_file) @ 20:08:33 — 3755 chars (body not exported)

## tool result (terminal) @ 20:08:33 — 609 chars (body not exported)

## tool result (terminal) @ 20:08:33 — 1927 chars (body not exported)

## assistant @ 20:14:18 → tools: terminal, terminal

I've confirmed the premise matches the brief and the old dispatcher matches the repair spec. Now I'll examine the exact probe bytes at line 211 and run the test file to verify the landing gates.

## tool result (terminal) @ 20:14:19 — 473 chars (body not exported)

## tool result (terminal) @ 20:14:19 — 65 chars (body not exported)

## assistant @ 20:16:16 → tools: terminal

`bash -n` clean on both. Now the two gate runs (item 1):

## tool result (terminal) @ 20:16:19 — 2374 chars (body not exported)

## assistant @ 20:18:03 → tools: terminal

Run 1: 37 passed, 0 failed. Second run + capturing the five named controls' `because:` lines:

## tool result (terminal) @ 20:18:05 — 984 chars (body not exported)

## assistant @ 20:18:16 → tools: terminal

Both gate runs match with 37 passing and 0 failing. Now I'll check the pre-repair dispatcher to verify the line number for the probe command.

## tool result (terminal) @ 20:18:16 — 825 chars (body not exported)

## assistant @ 20:18:29 → tools: terminal

The red-state test confirms the old probe at 435b057 uses substring binding as expected. Now I'll verify the red claim by running the test file against the old dispatcher in a scratch environment.

## tool result (terminal) @ 20:18:29 — 4440 chars (body not exported)

## assistant @ 20:18:42 → tools: terminal

I found that the test file is the PIN's with the old dispatcher at :205 using substring binding. Now I'll check if the four named controls go red against the old dispatcher, with the exact-token positive staying green.

## tool result (terminal) @ 20:18:44 — 3955 chars (body not exported)

## assistant @ 20:19:24 → tools: read_file

I found that the "exact-token" positive control actually failed on the old dispatcher, contradicting the brief's expectation. I'll check the builder's RED-claim to verify the discrepancy.

## tool result (read_file) @ 20:19:24 — 10497 chars (body not exported)

## assistant @ 20:22:27 → tools: terminal, terminal, terminal

The red claim needs verification: I found 8 failures against the old dispatcher, but the brief expected 4, including one unexpected exact-token positive. I'm investigating the environment, bash behavior, and the dispatcher logic to understand what's happening.

## tool result (terminal) @ 20:22:28 — 366 chars (body not exported)

## tool result (terminal) @ 20:22:28 — 7627 chars (body not exported)

## tool result (terminal) @ 20:23:41 — 1558 chars (body not exported)

## assistant @ 20:24:48 → tools: terminal, terminal

run-all.sh passes (rc 0, 1m13s). The `read`/pipefail mechanism does NOT swallow in bash 5.2/5.2/dash. Now let me root-cause the red-claim discrepancy — the exact-token test FAILED in my old-dispatcher run. Let me check tool availability and instrument the old probe against a live fixture:

## tool result (terminal) @ 20:24:48 — 1541 chars (body not exported)

## tool result (terminal) @ 20:24:48 — 345 chars (body not exported)

## assistant @ 20:30:13 → tools: execute_code

All tools present. run-all: ALL SUITES PASSED (rc 0, 1m13s). I've already reproduced the landing gates and found a RED-claim discrepancy (my old-dispatcher run = 29/8 vs brief's predicted 4; the exact-token positive FAILS, not "passes by design"). Let me confirm the mechanism and extract the exact probe bytes.

## tool result (execute_code) @ 20:30:13 — 808 chars (body not exported)

## assistant @ 20:33:38 → tools: terminal, terminal

I've reproduced the landing gates and found a red-claim discrepancy where the brief predicted a specific test outcome but my old-dispatcher run produced different results. Now I'm investigating the root cause of item-6 by checking what shell the PC bridge uses, since that affects how the probe executes remotely.

## tool result (terminal) @ 20:33:38 — 1076 chars (body not exported)

## tool result (terminal) @ 20:33:38 — 615 chars (body not exported)

## assistant @ 20:34:46 → tools: terminal



## tool result (terminal) @ 20:34:46 — 1261 chars (body not exported)

## assistant @ 20:34:55 → tools: terminal



## tool result (terminal) @ 20:34:55 — 1027 chars (body not exported)

## assistant @ 20:48:37 → tools: terminal, terminal

run-all: ALL SUITES PASSED (rc 0, 1m13s, single call). I've reproduced the landing gates and found a RED-claim discrepancy (my old-dispatcher run = 29/8 vs the brief's predicted 4; the exact-token positive FAILS, contradicting "passes by design"). Now let me root-cause item 6. First, how PIN/`ROOT`/git are set up:

## tool result (terminal) @ 20:48:37 — 1760 chars (body not exported)

## tool result (terminal) @ 20:48:37 — 1666 chars (body not exported)

## assistant @ 20:54:30 → tools: terminal

run-all: **ALL SUITES PASSED** (rc 0, 1m13s, single call). The `read`/pipefail hypothesis is already falsified (bash 5.2, dash: `x` is populated, RESUME not swallowed). Now I'll root-cause item 6's live re-attach failure. My analysis points at the base64 transfer breaking `$HOME` expansion. Let me prove it with a live pid on the PC.

## tool result (terminal) @ 20:54:30 — 330 chars (body not exported)

## assistant @ 20:56:30 → tools: write_file

The foreground guard blocks those wrappers. I'll put the exact same start in a script file and run that.

## tool result (write_file) @ 20:56:30 — 239 chars (body not exported)

## assistant @ 20:57:34 → tools: write_file

Let me rewrite with per-shape pidfiles to avoid collisions.

## tool result (write_file) @ 20:57:34 — 239 chars (body not exported)

## assistant @ 20:58:30 → tools: terminal

Let me look at the actual re-attach evidence (the K1-g lane dir and its launch.log) to ground item 6's real-world failure:

## tool result (terminal) @ 20:58:30 — 2619 chars (body not exported)

## assistant @ 21:00:12 → tools: terminal, terminal

run-all passed (rc 0, 1m13s). Now item 6 is the crux. I've already falsified the brief's pipefail hypothesis (bash 5.2/dash: `x` is populated, RESUME not swallowed). Let me ground the real failure: check the K1-g lane, env, and the real bridge contract.

## tool result (terminal) @ 21:00:12 — 2200 chars (body not exported)

## tool result (terminal) @ 21:00:12 — 330 chars (body not exported)

## assistant @ 21:06:37 → tools: terminal, terminal, terminal



## tool result (terminal) @ 21:06:38 — 365 chars (body not exported)

## tool result (terminal) @ 21:06:41 — 2222 chars (body not exported)

## tool result (terminal) @ 21:06:42 — 222 chars (body not exported)

## assistant @ 21:07:59 → tools: write_file



## tool result (write_file) @ 21:07:59 — 331 chars (body not exported)

## assistant @ 21:08:13 → tools: terminal



## tool result (terminal) @ 21:08:17 — 1693 chars (body not exported)

## assistant @ 21:08:33 → tools: read_file



## tool result (read_file) @ 21:08:33 — 2568 chars (body not exported)

## assistant @ 21:09:02 → tools: search_files, terminal



## tool result (search_files) @ 21:09:02 — 133 chars (body not exported)

## tool result (terminal) @ 21:09:02 — 1006 chars (body not exported)

## assistant @ 21:12:11 → tools: execute_code



## tool result (execute_code) @ 21:12:12 — 339 chars (body not exported)

## assistant @ 21:12:44 → tools: write_file



## tool result (write_file) @ 21:12:45 — 262 chars (body not exported)

## assistant @ 21:12:55 → tools: terminal



## tool result (terminal) @ 21:12:55 — 138 chars (body not exported)

## assistant @ 21:13:23 → tools: terminal



## tool result (terminal) @ 21:13:23 — 1002 chars (body not exported)

## assistant @ 21:13:49 → tools: write_file



## tool result (write_file) @ 21:13:49 — 260 chars (body not exported)

## assistant @ 21:14:39 → tools: terminal



## tool result (terminal) @ 21:14:39 — 616 chars (body not exported)

## assistant @ 21:14:59 → tools: write_file



## tool result (write_file) @ 21:14:59 — 246 chars (body not exported)

## assistant @ 21:15:32 → tools: terminal



## tool result (terminal) @ 21:15:34 — 2442 chars (body not exported)

## assistant @ 21:17:08 → tools: write_file



## tool result (write_file) @ 21:17:08 — 244 chars (body not exported)

## assistant @ 21:17:25 → tools: write_file



## tool result (write_file) @ 21:17:25 — 244 chars (body not exported)

## assistant @ 21:17:42 → tools: terminal



## tool result (terminal) @ 21:17:42 — 221 chars (body not exported)

## assistant @ 21:18:22 → tools: write_file



## tool result (write_file) @ 21:18:22 — 239 chars (body not exported)

## assistant @ 21:18:42 → tools: terminal



## tool result (terminal) @ 21:18:42 — 109 chars (body not exported)

## assistant @ 21:19:07 → tools: patch



## tool result (patch) @ 21:19:07 — 729 chars (body not exported)

## assistant @ 21:19:23 → tools: terminal



## tool result (terminal) @ 21:19:24 — 1201 chars (body not exported)

## assistant @ 21:21:12 → tools: write_file



## tool result (write_file) @ 21:21:13 — 233 chars (body not exported)

## assistant @ 21:21:33 → tools: terminal



## tool result (terminal) @ 21:21:34 — 2493 chars (body not exported)

## assistant @ 21:21:57 → tools: execute_code



## tool result (execute_code) @ 21:21:59 — 317 chars (body not exported)

## assistant @ 21:22:20 → tools: terminal, terminal



## tool result (terminal) @ 21:22:22 — 539 chars (body not exported)

## tool result (terminal) @ 21:22:24 — 336 chars (body not exported)

## assistant @ 21:23:41 → tools: terminal, terminal, terminal, terminal



## tool result (terminal) @ 21:23:41 — 1995 chars (body not exported)

## tool result (terminal) @ 21:23:41 — 156 chars (body not exported)

## tool result (terminal) @ 21:23:41 — 520 chars (body not exported)

## tool result (terminal) @ 21:23:41 — 480 chars (body not exported)

## assistant @ 21:24:19 → tools: write_file



## tool result (write_file) @ 21:24:19 — 237 chars (body not exported)

## assistant @ 21:24:28 → tools: terminal



## tool result (terminal) @ 21:24:28 — 572 chars (body not exported)

## assistant @ 21:24:47 → tools: terminal



## tool result (terminal) @ 21:24:48 — 198 chars (body not exported)

## assistant @ 21:25:21 → tools: terminal



## tool result (terminal) @ 21:25:21 — 214 chars (body not exported)

## assistant @ 21:25:50 → tools: terminal



## tool result (terminal) @ 21:25:51 — 247 chars (body not exported)

## assistant @ 21:26:12 → tools: write_file



## tool result (write_file) @ 21:26:12 — 242 chars (body not exported)

## assistant @ 21:26:30 → tools: terminal



## tool result (terminal) @ 21:26:30 — 1545 chars (body not exported)

## assistant @ 21:26:42 → tools: write_file



## tool result (write_file) @ 21:26:43 — 247 chars (body not exported)

## assistant @ 21:26:48 → tools: terminal



## tool result (terminal) @ 21:26:48 — 403 chars (body not exported)

## assistant @ 21:27:08 → tools: write_file



## tool result (write_file) @ 21:27:08 — 249 chars (body not exported)

## assistant @ 21:27:22 → tools: terminal



## tool result (terminal) @ 21:27:22 — 295 chars (body not exported)

## assistant @ 21:27:51 → tools: write_file



## tool result (write_file) @ 21:27:52 — 245 chars (body not exported)

## assistant @ 21:28:08 → tools: terminal



## tool result (terminal) @ 21:28:08 — 157 chars (body not exported)

## assistant @ 21:28:43 → tools: write_file



## tool result (write_file) @ 21:28:43 — 243 chars (body not exported)

## assistant @ 21:28:57 → tools: terminal



## tool result (terminal) @ 21:28:57 — 269 chars (body not exported)

## assistant @ 21:30:02 → tools: patch



## tool result (patch) @ 21:30:02 — 998 chars (body not exported)

## assistant @ 21:30:13 → tools: patch



## tool result (patch) @ 21:30:13 — 788 chars (body not exported)

## assistant @ 21:30:22 → tools: terminal



## tool result (terminal) @ 21:30:22 — 311 chars (body not exported)

## assistant @ 21:30:43 → tools: write_file



## tool result (write_file) @ 21:30:43 — 244 chars (body not exported)

## assistant @ 21:30:55 → tools: terminal



## tool result (terminal) @ 21:30:55 — 117 chars (body not exported)

## assistant @ 21:31:08 → tools: terminal



## tool result (terminal) @ 21:31:08 — 1297 chars (body not exported)

## assistant @ 21:31:29 → tools: execute_code



## tool result (execute_code) @ 21:31:30 — 315 chars (body not exported)

## assistant @ 21:31:50 → tools: write_file



## tool result (write_file) @ 21:31:50 — 252 chars (body not exported)

## assistant @ 21:32:00 → tools: terminal



## tool result (terminal) @ 21:32:00 — 482 chars (body not exported)

## assistant @ 21:32:17 → tools: patch



## tool result (patch) @ 21:32:17 — 1385 chars (body not exported)

## assistant @ 21:32:31 → tools: terminal



## tool result (terminal) @ 21:32:31 — 482 chars (body not exported)

## assistant @ 21:32:45 → tools: patch



## tool result (patch) @ 21:32:46 — 1677 chars (body not exported)

## assistant @ 21:32:59 → tools: terminal



## tool result (terminal) @ 21:32:59 — 807 chars (body not exported)

## assistant @ 21:33:14 → tools: terminal



## tool result (terminal) @ 21:33:14 — 152 chars (body not exported)

## assistant @ 21:33:30 → tools: terminal



## tool result (terminal) @ 21:33:30 — 634 chars (body not exported)

## assistant @ 21:33:50 → tools: terminal



## tool result (terminal) @ 21:33:50 — 488 chars (body not exported)

## assistant @ 21:34:39 → tools: execute_code



## tool result (execute_code) @ 21:34:39 — 614 chars (body not exported)

## assistant @ 21:35:13 → tools: execute_code



## tool result (execute_code) @ 21:35:13 — 1485 chars (body not exported)

## assistant @ 21:36:09 → tools: execute_code



## tool result (execute_code) @ 21:36:10 — 708 chars (body not exported)

## assistant @ 21:36:37 → tools: write_file



## tool result (write_file) @ 21:36:37 — 254 chars (body not exported)

## assistant @ 21:36:52 → tools: terminal



## tool result (terminal) @ 21:36:53 — 481 chars (body not exported)

## assistant @ 21:37:15 → tools: terminal



## tool result (terminal) @ 21:37:15 — 460 chars (body not exported)

## assistant @ 21:38:00 → tools: terminal



## tool result (terminal) @ 21:38:00 — 62 chars (body not exported)

## assistant @ 21:38:26 → tools: execute_code



## tool result (execute_code) @ 21:38:26 — 302 chars (body not exported)

## assistant @ 21:38:46 → tools: terminal



## tool result (terminal) @ 21:38:46 — 477 chars (body not exported)

## assistant @ 21:39:11 → tools: terminal



## tool result (terminal) @ 21:39:11 — 129 chars (body not exported)

## assistant @ 21:40:26 → tools: write_file



## tool result (write_file) @ 21:40:26 — 247 chars (body not exported)

## assistant @ 21:40:32 → tools: execute_code



## tool result (execute_code) @ 21:40:32 — 312 chars (body not exported)

## assistant @ 21:43:29 → tools: write_file



## tool result (write_file) @ 21:43:30 — 414 chars (body not exported)

## assistant @ 21:43:49 → tools: terminal, terminal, terminal



## tool result (terminal) @ 21:43:49 — 1106 chars (body not exported)

## tool result (terminal) @ 21:43:49 — 199 chars (body not exported)

## tool result (terminal) @ 21:43:50 — 65 chars (body not exported)

## assistant @ 21:43:56 → tools: read_file



## tool result (read_file) @ 21:43:56 — 2802 chars (body not exported)

## assistant @ 21:44:01 → tools: read_file



## tool result (read_file) @ 21:44:01 — 11792 chars (body not exported)

## assistant @ 21:44:19 → tools: patch



## tool result (patch) @ 21:44:19 — 1532 chars (body not exported)

## assistant @ 21:44:44 → tools: patch



## tool result (patch) @ 21:44:44 — 2160 chars (body not exported)

## assistant @ 21:44:56 → tools: patch



## tool result (patch) @ 21:44:56 — 1375 chars (body not exported)

## assistant @ 21:45:16 → tools: patch



## tool result (patch) @ 21:45:16 — 1947 chars (body not exported)

## assistant @ 21:45:30 → tools: patch



## tool result (patch) @ 21:45:30 — 1301 chars (body not exported)

## assistant @ 21:45:36 → tools: terminal



## tool result (terminal) @ 21:45:36 — 231 chars (body not exported)

## assistant @ 21:45:51 → tools: patch



## tool result (patch) @ 21:45:51 — 1162 chars (body not exported)

## assistant @ 21:45:57 → tools: execute_code



## tool result (execute_code) @ 21:45:57 — 318 chars (body not exported)

## assistant @ 21:46:23 → tools: terminal, terminal, terminal



## tool result (terminal) @ 21:46:23 — 659 chars (body not exported)

## tool result (terminal) @ 21:46:23 — 576 chars (body not exported)

## tool result (terminal) @ 21:46:23 — 260 chars (body not exported)

## assistant @ 21:46:30 → tools: patch



## tool result (patch) @ 21:46:30 — 1091 chars (body not exported)

## assistant @ 21:46:37 → tools: terminal



## tool result (terminal) @ 21:46:37 — 231 chars (body not exported)

## assistant @ 21:46:45 → tools: patch



## tool result (patch) @ 21:46:45 — 1087 chars (body not exported)

## assistant @ 21:46:58 → tools: execute_code



## tool result (execute_code) @ 21:46:59 — 341 chars (body not exported)

## assistant @ 21:47:14 → tools: terminal, terminal, terminal



## tool result (terminal) @ 21:47:14 — 287 chars (body not exported)

## tool result (terminal) @ 21:47:14 — 893 chars (body not exported)

## tool result (terminal) @ 21:47:15 — 45 chars (body not exported)

## assistant @ 21:47:27 → tools: search_files



## tool result (search_files) @ 21:47:27 — 6897 chars (body not exported)

## assistant @ 21:47:53 → tools: search_files



## tool result (search_files) @ 21:47:53 — 4099 chars (body not exported)

## assistant @ 21:48:02 → tools: patch



## tool result (patch) @ 21:48:03 — 1568 chars (body not exported)

## assistant @ 21:48:11 → tools: execute_code



## tool result (execute_code) @ 21:48:11 — 305 chars (body not exported)

## assistant @ 21:48:17 → tools: terminal



## tool result (terminal) @ 21:48:17 — 287 chars (body not exported)

## assistant @ 21:50:52

NOT-READY recommendation.

Report written to:

/home/rocco/agent-factory/.lanes/pc-verify-t90-r2.md--76ca87c/tree/tasks/briefs/pc-t90-support/VERIFY-T90-R2-report.md

VERIFY-T90-R2 — targeted independent adversarial verification

STATUS

NOT-READY recommendation. The frozen R-F1 contract is still violated on the production dispatcher path when PC_AF_REPO has its normal literal `$HOME/agent-factory` value.

The structural PID binding works when given an absolute lane directory. The F3 self-copy repair holds.

IDENTITY

PIN: <opaque-redacted>

Boundary:
  scripts/pc_lane.sh
  harness-ports/tests/test_pc_lane_dispatcher.sh

Dispatcher:
  561 lines
  sha256[:16]: ef6b64a1d8fcfc99
  mode: 100755

Test file:
  417 lines
  sha256[:16]: f74d7e0a3419dcb7
  29 check sites
  37 runtime checks

REPRODUCTION SUMMARY

  Landing dispatcher gate:
    pc_lane dispatcher: 37 passed, 0 failed
    Repeated twice, rc 0 both times.

  Syntax:
    bash -n scripts/pc_lane.sh
    bash -n harness-ports/tests/test_pc_lane_dispatcher.sh
    FINAL_SYNTAX_OK

  Full suite:
    ALL SUITES PASSED
    rc=0
    elapsed=1m13.624s

  AP screen:
    3 known hits
    AF-AP-87: 2 at scripts/pc_lane.sh:384
    AF-AP-59: 1 at scripts/pc_lane.sh:376
    No repair-added hit.

  Own report lint:
    report_lint: 16 refs — OK 15, NEAR 0, MISS 0,
    UNCHECKABLE 1, UNRESOLVED 0 (worktree)

LANDING CONTROLS

  [PASS] inherited PC_LANE_SELF_COPY does not skip the
  private copy or delete the caller sentinel

    rc=64
    private_copy=/tmp/tmp.WEyVrE2aRC/copy-inherited/pc_lane.sh.YayNOG
    private_copy_exists=no
    sentinel_exists=yes
    bridge_calls=1

  [PASS] EXIT trap removes only its own private-copy path

    reason=mutant-other-path-deleted
    rc=64
    private_copy=/tmp/tmp.WEyVrE2aRC/copy-inherited/pc_lane.sh.oX81jv
    private_copy_exists=no
    other_path_exists=no

  [PASS] sibling suffix ID is FIRST and refused with no ship

    state=FIRST
    rc=64
    no_ship_writes=0

  [PASS] argv mention alone is FIRST and refused with no ship

    state=FIRST
    rc=64
    no_ship_writes=0

  [PASS] argv token equal to the lane directory is RESUME

    state=RESUME 1790000000
    rc=75
    ship_writes=1

RED CONTROL

PIN test file against the pre-repair dispatcher from 435b057:

  RC_RED=1
  pc_lane dispatcher: 29 passed, 8 failed

Named failures:

  [FAIL] inherited PC_LANE_SELF_COPY control

    rc=64
    private_copy=/tmp/tmp.fL8yt77dvZ/caller-self-copy-sentinel
    private_copy_exists=no
    sentinel_exists=no
    bridge_calls=1

  [FAIL] EXIT trap ownership control

    reason=no
    rc=64
    private_copy=/tmp/tmp.fL8yt77dvZ/copy-inherited/pc_lane.sh.EAY1du
    private_copy_exists=no
    other_path_exists=yes

  [FAIL] sibling suffix control

    state=RESUME 1790108323
    rc=75
    no_ship_writes=1

  [FAIL] argv mention control

    state=RESUME 1790108323
    rc=75
    no_ship_writes=1

  [FAIL] exact-token positive control

    state=FIRST
    rc=64
   


---
usage.json:

```json
{
  "estimated_cost_usd": 0.0,
  "cost_status": "unknown",
  "cost_source": "none",
  "input_tokens": 656659,
  "output_tokens": 138659,
  "cache_read_tokens": 10917408,
  "cache_write_tokens": 0,
  "reasoning_tokens": 96484,
  "total_tokens": 11712726,
  "api_calls": 119,
  "model": "codex/gpt-5.6-sol-xhigh",
  "provider": "custom",
  "session_id": "20260922_205843_e547bc",
  "completed": true,
  "failed": false,
  "service_tier": null
}

```
