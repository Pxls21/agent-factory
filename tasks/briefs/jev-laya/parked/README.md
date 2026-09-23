# Parked: the PCJ1-R1 long-output wrapper (2026-09-23)

`long-output.sh` and `test_long_output.sh` were built by the coordinator on 2026-09-22 as PCJ1-R1: a model-invoked
wrapper that runs a skim-only command through jev-pruner's Codex entry point when the local Laya endpoint answers
`/health` with `"ok": true` AND the pinned revision `1c5edc17a7acd8701df6fc341c0d179f1c62c982`, and runs the command
unchanged otherwise. Its test held 9 checks (`long-output: 9 passed, 0 failed` twice); mutants n1-n4 and m5 were each
killed by a named check.

It is PARKED, not wired, because the live PC smoke on 2026-09-23 showed the pruner cannot engage on a Hermes lane:

- jev-pruner prunes only after `readTranscript(sessionId)` reads `~/.cache/jev-pruner/codex/<id>.json`, a pointer
  that only its own Codex PreToolUse hook writes (`dist/codex/context.js`, `dist/codex/prune.js` at 47d017c). Hermes
  lanes never write it, and the PC has no Codex install (`/home/rocco/.codex` absent).
- Measured on the PC through this wrapper: a 20,000-line output (108,894 bytes) came back whole, the endpoint's
  `calls` counter stayed at 10, and no `.jev-pruner` archive directory was written. The pruner returned before it
  reached the endpoint, so "pruner ON" behaved exactly like OFF (AF-AP-121).
- Even with a pointer, the pruner's per-request deadline is a fixed 30 s, and PCJ1's own smoke (with a planted
  pointer) did not see the endpoint answer inside it on CPU.

The files are kept here as the starting point if the owner chooses the Hermes adapter option. They are not on any
path: nothing sources, runs or names them, and the test expects the old location `harness-ports/bin/long-output.sh`.
