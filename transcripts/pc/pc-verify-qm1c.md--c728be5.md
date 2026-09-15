# Hermes lane session 20260915_203221_c3f607

- model: agentfactory-verify
- started: 2026-09-15T19:32:22.096331+00:00
- cwd: /home/rocco/agent-factory/.lanes/pc-verify-qm1c.md--c728be5/tree
- messages: 121; tool calls: 82
- tokens in/out/cache_read/reasoning: 153833/37027/4167680/19250

## user @ 19:32:21

<!-- HARNESS PORT of .claude/agents/adversarial-verifier.md — see docs/HARNESS-PORTS.md.
     The body below is carried over UNCHANGED; only the Claude-Code frontmatter was
     removed. The model pin does not survive the port: the PC harness serves ONE
     model, so all three lane roles run on the same model and the coordinator-side
     routing table does not apply there.

     CONSEQUENCE, and it is the important one: on a single-model harness a lane
     cannot supply its own independent verification. A build lane's output is a
     PROPOSAL until the sandbox-side adversarial-verifier lane grades it. Never
     self-accept, and never issue a gate verdict.

     Codex loads this as `developer_instructions` via .codex/agents/adversarial-verifier.toml.
     Hermes has no role mechanism, so harness-ports/bin/pc-lane.sh prepends this
     file to the brief instead. -->

# Lane role: adversarial-verifier

<!-- Adapted from Lunarsong/Claude-Opus-5-tools adversarial-review (CC0) + this repo's Phase-5
     verify discipline. Provenance: docs/THIRD-PARTY-AGENT-TOOLS.md -->

Your job is to make the change fail, not to confirm it works. The author's report is a list of
claims; reproduce every claim you rely on. You have no stake in the change passing.

## Minimum attack set

1. **Contract, not self-declared cases.** Grade against the increment's full contract (the
   negotiated assertion list / seed acceptance criteria / brief evidence demands) — the builder's
   own tests prove only what the builder thought of.
2. **Fresh gates, real counts.** Re-run the suites yourself; verify the suite RAN by its test
   counts (a filter matching nothing exits 0). Read `${PIPESTATUS[0]}` on piped runs.
3. **Red-green.** Reproduce the red state for new tests (revert the change on a SCRATCHPAD COPY,
   keep the tests, observe the failure). A test that was never red is a claim. Hunt tautologies —
   a control assertion that stays green in the red build. NEVER `git checkout/restore/stash` a
   tree carrying uncommitted work — scratchpad copies only.
4. **Hostile inputs.** Anything touching externally-sourced values gets the fail-open class:
   NaN, ±inf, empty, zero-range, post-scaling degenerates, timeouts, stale/truncated identifiers.
   A hang is a finding. This repo's incident log says NaN wormholes bit TWICE — always test the
   whole unusable class, not a bare `<= 0`.
5. **Mutation audit.** Inject targeted bugs one at a time (tautology the check, delete the guard,
   drop the wiring); a gate that stays green over a mutant is hollow. Restore from scratchpad
   copies; end `git status`-clean; never run a guard-disabling mutant pointed at a real protected
   resource.
6. **Reachability.** "Exists" ≠ "wired": trace from the LIVE entry point; an injectable-but-never-
   injected seam and a sink-of-throwaway-default are reachability hollow-greens. Verify identity
   (the exact entity claimed), state (the artifact changed), and that the identity key COVERS the
   attribut

## assistant @ 19:32:30 → tools: read_file



## tool result (read_file) @ 19:32:30 — 6035 chars (body not exported)

## assistant @ 19:32:43 → tools: skill_view, skill_view, skill_view, skill_view, skill_view, read_file, terminal



## tool result (skill_view) @ 19:32:43 — 5011 chars (body not exported)

## tool result (skill_view) @ 19:32:43 — 24119 chars (body not exported)

## tool result (skill_view) @ 19:32:43 — 10636 chars (body not exported)

## tool result (skill_view) @ 19:32:43 — 14477 chars (body not exported)

## tool result (skill_view) @ 19:32:43 — 37279 chars (body not exported)

## tool result (read_file) @ 19:32:43 — 5973 chars (body not exported)

## tool result (terminal) @ 19:32:44 — 170 chars (body not exported)

## assistant @ 19:32:58 → tools: write_file



## tool result (write_file) @ 19:32:58 — 326 chars (body not exported)

## assistant @ 19:33:15 → tools: terminal, terminal, terminal, terminal, terminal, terminal



## tool result (terminal) @ 19:33:18 — 4708 chars (body not exported)

## tool result (terminal) @ 19:33:22 — 11602 chars (body not exported)

## tool result (terminal) @ 19:33:29 — 159 chars (body not exported)

## tool result (terminal) @ 19:33:31 — 237 chars (body not exported)

## tool result (terminal) @ 19:33:31 — 2049 chars (body not exported)

## tool result (terminal) @ 19:33:32 — 2033 chars (body not exported)

## assistant @ 19:33:49 → tools: read_file, read_file, read_file, read_file, read_file, terminal, terminal, terminal



## tool result (read_file) @ 19:33:49 — 4812 chars (body not exported)

## tool result (read_file) @ 19:33:49 — 16598 chars (body not exported)

## tool result (read_file) @ 19:33:49 — 7792 chars (body not exported)

## tool result (read_file) @ 19:33:49 — 10648 chars (body not exported)

## tool result (read_file) @ 19:33:49 — 12325 chars (body not exported)

## tool result (terminal) @ 19:33:52 — 17907 chars (body not exported)

## tool result (terminal) @ 19:33:55 — 15035 chars (body not exported)

## tool result (terminal) @ 19:33:55 — 22581 chars (body not exported)

## assistant @ 19:34:38 → tools: terminal, read_file, read_file, read_file, terminal, terminal



## tool result (terminal) @ 19:34:41 — 9978 chars (body not exported)

## tool result (read_file) @ 19:34:41 — 1575 chars (body not exported)

## tool result (read_file) @ 19:34:41 — 10624 chars (body not exported)

## tool result (read_file) @ 19:34:41 — 9401 chars (body not exported)

## tool result (terminal) @ 19:34:41 — 228 chars (body not exported)

## tool result (terminal) @ 19:34:41 — 79 chars (body not exported)

## assistant @ 19:35:51 → tools: read_file, read_file, read_file, terminal, terminal



## tool result (read_file) @ 19:35:51 — 4306 chars (body not exported)

## tool result (read_file) @ 19:35:51 — 12946 chars (body not exported)

## tool result (read_file) @ 19:35:51 — 6172 chars (body not exported)

## tool result (terminal) @ 19:35:51 — 650 chars (body not exported)

## tool result (terminal) @ 19:35:51 — 56 chars (body not exported)

## assistant @ 19:37:00 → tools: write_file



## tool result (write_file) @ 19:37:01 — 339 chars (body not exported)

## assistant @ 19:37:11 → tools: terminal, terminal, terminal, terminal



## tool result (terminal) @ 19:37:11 — 101 chars (body not exported)

## tool result (terminal) @ 19:37:12 — 83 chars (body not exported)

## tool result (terminal) @ 19:37:18 — 3587 chars (body not exported)

## tool result (terminal) @ 19:38:37 — 1127 chars (body not exported)

## assistant @ 19:39:59 → tools: terminal, terminal, terminal, terminal



## tool result (terminal) @ 19:39:59 — 240 chars (body not exported)

## tool result (terminal) @ 19:39:59 — 235 chars (body not exported)

## tool result (terminal) @ 19:40:00 — 669 chars (body not exported)

## tool result (terminal) @ 19:40:01 — 146 chars (body not exported)

## assistant @ 19:41:21 → tools: write_file



## tool result (write_file) @ 19:41:22 — 331 chars (body not exported)

## assistant @ 19:41:28 → tools: patch



## tool result (patch) @ 19:41:29 — 1349 chars (body not exported)

## assistant @ 19:41:33 → tools: terminal



## tool result (terminal) @ 19:41:33 — 97 chars (body not exported)

## assistant @ 19:41:37 → tools: terminal



## tool result (terminal) @ 19:42:07 — 411 chars (body not exported)

## assistant @ 19:43:18 → tools: read_file, read_file, read_file, terminal, terminal, terminal



## tool result (read_file) @ 19:43:18 — 370 chars (body not exported)

## tool result (read_file) @ 19:43:18 — 526 chars (body not exported)

## tool result (read_file) @ 19:43:18 — 526 chars (body not exported)

## tool result (terminal) @ 19:43:19 — 210 chars (body not exported)

## tool result (terminal) @ 19:43:19 — 83 chars (body not exported)

## tool result (terminal) @ 19:43:26 — 3587 chars (body not exported)

## assistant @ 19:43:34 → tools: terminal



## tool result (terminal) @ 19:43:34 — 408 chars (body not exported)

## assistant @ 19:44:38 → tools: terminal, terminal, terminal, terminal



## tool result (terminal) @ 19:44:39 — 147 chars (body not exported)

## tool result (terminal) @ 19:44:48 — 521 chars (body not exported)

## tool result (terminal) @ 19:44:48 — 1570 chars (body not exported)

## tool result (terminal) @ 19:44:48 — 139 chars (body not exported)

## assistant @ 19:45:29 → tools: write_file



## tool result (write_file) @ 19:45:29 — 415 chars (body not exported)

## assistant @ 19:45:37 → tools: write_file



## tool result (write_file) @ 19:45:37 — 326 chars (body not exported)

## assistant @ 19:45:52 → tools: read_file



## tool result (read_file) @ 19:45:52 — 8138 chars (body not exported)

## assistant @ 19:46:07 → tools: terminal, terminal, terminal



## tool result (terminal) @ 19:46:09 — 65 chars (body not exported)

## tool result (terminal) @ 19:46:09 — 198 chars (body not exported)

## tool result (terminal) @ 19:46:09 — 98 chars (body not exported)

## assistant @ 19:46:15 → tools: terminal



## tool result (terminal) @ 19:46:15 — 1200 chars (body not exported)

## assistant @ 19:46:28 → tools: patch



## tool result (patch) @ 19:46:28 — 2052 chars (body not exported)

## assistant @ 19:46:35 → tools: patch



## tool result (patch) @ 19:46:36 — 1582 chars (body not exported)

## assistant @ 19:46:53 → tools: patch



## tool result (patch) @ 19:46:53 — 3892 chars (body not exported)

## assistant @ 19:46:58 → tools: patch



## tool result (patch) @ 19:46:59 — 1616 chars (body not exported)

## assistant @ 19:47:09 → tools: patch



## tool result (patch) @ 19:47:09 — 1546 chars (body not exported)

## assistant @ 19:47:22 → tools: patch



## tool result (patch) @ 19:47:22 — 2528 chars (body not exported)

## assistant @ 19:47:27 → tools: terminal



## tool result (terminal) @ 19:47:28 — 1243 chars (body not exported)

## assistant @ 19:47:36 → tools: patch



## tool result (patch) @ 19:47:36 — 2397 chars (body not exported)

## assistant @ 19:47:42 → tools: patch



## tool result (patch) @ 19:47:42 — 1489 chars (body not exported)

## assistant @ 19:47:49 → tools: terminal



## tool result (terminal) @ 19:47:49 — 725 chars (body not exported)

## assistant @ 19:47:54 → tools: patch



## tool result (patch) @ 19:47:54 — 1495 chars (body not exported)

## assistant @ 19:48:00 → tools: terminal



## tool result (terminal) @ 19:48:00 — 725 chars (body not exported)

## assistant @ 19:48:05 → tools: patch



## tool result (patch) @ 19:48:05 — 1492 chars (body not exported)

## assistant @ 19:48:11 → tools: terminal



## tool result (terminal) @ 19:48:11 — 246 chars (body not exported)

## assistant @ 19:48:19 → tools: terminal, terminal, terminal



## tool result (terminal) @ 19:48:19 — 253 chars (body not exported)

## tool result (terminal) @ 19:48:19 — 650 chars (body not exported)

## tool result (terminal) @ 19:48:20 — 147 chars (body not exported)

## assistant @ 19:49:11

# VERIFY-QM1-c — adversarial verification of QM1-c (landed at `c728be5`)

FINDINGS ONLY. This cloud verify lane reports no merge verdict.

## Finding 1 — BLOCKER — failed/aborted runs can be rendered as valid matrix evidence

M:409 (`candidate`) accepts a cell solely from `result.json` plus its identity and summary fields at M:414 (`data.get`). It does not require a completion marker, reject `run-error`, or otherwise bind the table reader to a successfully completed launcher run. R:60 (`RESULT_FILE`) is written by the Python run at R:151-157 (`load generator failed`) before later post-processing, and the launcher has no completion marker at R:161-170 (`result.write_text`).

Repro (fresh synthetic cell, no live seam): create a cell directory containing a fully valid `result.json` and no run marker, then run the production table command. The observed output was `MARKER_EXISTS False`, a rendered A row, and exit `0`. Adding either `run-error` or an arbitrary `run-complete` file also yielded `TABLE_RC 0`. This contradicts the brief’s V1 requirement that a `result.json` whose run did not complete be rejected.

Minimal fix: write an immutable per-run completion record only after result post-processing and successful restoration, bind it into the cell record, and make `_load_cell` require that matching record while rejecting an error/unfinished state. Add a true failed-after-result fixture through `qwen-matrix.sh`, not only an existing-directory refusal before creation.

## Finding 2 — SHOULD-FIX — persisted unit identity checks format, not the actual unit bytes

M:417 (`argv_text`) through M:427 (`unit_sha`) verify only that `unit_sha256` is lower-case 64-hex. Unlike `argv_sha256` at M:424 (`hashlib.sha256`), it never recomputes it from a persisted unit-text artifact. The launcher writes only `unit-sha256` at R:69-72 (`UNIT_SHA`), not the exact rendered `UNIT_TEXT`.

Repro: a valid cell with `unit_sha256 = 'b' * 64` loads successfully: `ARBITRARY_LOWERCASE_UNIT_SHA_ACCEPTED bbbbb...`. A lower-case digest of unrelated bytes therefore passes as the claimed unit identity.

Minimal fix: persist the exact rendered unit text beside the cell result and recompute/compare its SHA-256 in `_load_cell`; test a canonical-looking lower-case SHA that does not match the persisted unit text.

## Reproduced controls and attack coverage

- V2 absence restoration: R:97-105 (`uninstall`) was exercised through the fake-only direct suite. X:145-150 (`QM_UNINSTALL_LEAVES_UNIT`) reported `13 passed, 0 failed`; its hostile fake-uninstall case returned rc `8` with `initially absent unit remains after restore`. A separately constructed present-unit fake whose baseline bytes differ from launcher defaults produced rc `8` and `baseline unit sha mismatch after restore`, so byte drift fails loud.
- V3 rotation: M:283-293 (`_count_reprefills`) raised the production `MatrixError` for same-inode truncation and a larger replacement; a simulated device change with the same inode was also re


---
usage.json:

```json
{
  "estimated_cost_usd": 0.0,
  "cost_status": "unknown",
  "cost_source": "none",
  "input_tokens": 153833,
  "output_tokens": 37027,
  "cache_read_tokens": 4167680,
  "cache_write_tokens": 0,
  "reasoning_tokens": 19250,
  "total_tokens": 4358540,
  "api_calls": 38,
  "model": "agentfactory-verify",
  "provider": "custom",
  "session_id": "20260915_203221_c3f607",
  "completed": true,
  "failed": false,
  "service_tier": null
}

```
