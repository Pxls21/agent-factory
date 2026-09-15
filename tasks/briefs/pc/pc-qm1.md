# PC lane — QM1 (the L1 concurrency-matrix runner: replay load generator + per-cell server runner + the matrix table)

PIN: 47549c7

Role: code-implementer. Route: the CLOUD build route (`HERMES_MODEL=agentfactory-build`, `HERMES_REASONING=ultra`) — the local slot
holds VERIFY-N5k and the model unit must not be touched. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/qwen-matrix-l1-load-generator.md` — READ IT WHOLE and build items 1-6 in order. Your worktree
IS `git archive <PIN>` plus the lane patch (the brief, this file, the pack `tasks/briefs/qwen-matrix-support/QM1-pack.md`);
`docs/research/findings/RESEARCH-FINDINGS-1-VERIFIED.md` (§4 = the matrix you are building the runner for) and
`harness-ports/bin/qwen-server.sh` are IN the archive. Save your report at `tasks/briefs/qwen-matrix-support/QM1-report.md` inside
your tree, draft after EACH item, and return it whole as your final message.

Venue notes specific to this build:
- The server is LIVE at `127.0.0.1:8080` under a verify lane: `/metrics`, `/props`, `/health` and `/tokenize` are read-only and
  allowed (keyed; the key file path is `~/.config/qwen-builder/api-key` — read it into a variable, never echo it); ONE chat completion
  of ≤ 64 tokens to prove the client works is allowed; NO load runs, NO restarts.
- The session exports are at `~/qwen-builder/ab/` (read-only): `n5k-medium-armA.md` 138,278 B, `n5k-xhigh-v3-armB.md` 217,751 B.
- Hermes's `terminal` tool caps ONE call at 420 s: `harness-ports/tests/run-all.sh` is ~2 minutes; run it in one foreground call.
