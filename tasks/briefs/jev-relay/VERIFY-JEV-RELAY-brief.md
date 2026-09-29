# VERIFY-JEV-RELAY: attack the scrubbing relay before the output pruner is pointed at it (task #373, D-109)

Written 2026-09-29 from 12:1xZ (clock read at 12:19:29Z) by the coordinator. Role: sandbox `adversarial-verifier`, model
opus. Do NOT spawn subagents. Return the WHOLE report as your final message (a report-file write is refused for
subagents).

The change under test: `scripts/jev_relay.py` and `tests/test_jev_relay.py`, landed GATED-PENDING-VERIFY and INERT
(nothing points at the relay; it is not running). Its landing commit's message is the builder's account: every claim a
hypothesis. The rulings: D-078 (codiv.ai is allowed for this work only after `transcript_export`'s scrubber) and D-109
(the owner: "just build the scrubber"), both in `docs/08_DECISION_LOG.md`.

Why it matters: once switched on, the installed output-pruner plugin (`fast-jev-output@fast-jev-output`, under
`/root/.claude/plugins/cache/fast-jev-output/`, READ only, never modify) sends every Bash output over its token
threshold, with a segment of the conversation, to this relay, and the relay sends it on to codiv.ai with the owner's
key. A secret that survives the relay leaves the machine. The switch-on sets the plugin's `pluginConfigs` options:
`baseUrl` = `http://127.0.0.1:47430/v1/systemone`, a placeholder `apiKey`, `model` = `openjev-latest`.

## What to attack

1. **Premise.** Re-run the PREMISE block below; on a difference, stop and report CONTRACT-INVALID.
2. **Nothing secret leaves.** Build hostile requests beyond the tests' shapes and measure what a fake upstream receives:
   every JSON position (nested lists, objects in lists, keys), JSON `\u` escapes, a secret split across two strings or
   two chunks (the plugin splits long lines: read `src/output.ts` for where it cuts, and build the cut it would make), a
   secret at a string's first or last byte, very long strings, non-UTF-8 and surrogate escapes, deep nesting (a
   `RecursionError` path: what does the caller get, and does anything leave?), and every secret class
   `transcript_export`'s rules name. For each shape: sent or not, and the reply.
3. **The value gate.** Which sources load at start (`transcript_export.KNOWN_VALUE_SOURCES` plus the key file); what the
   relay does when a source is missing, unreadable, a FIFO, or changes after start; whether an 8-byte window gives false
   refusals on ordinary Bash output (git and sha256 hex runs; measure on real outputs under a scratch dir, never on a
   secret file).
4. **The key.** It is read only from the key file and never printed, logged, put in argv, returned or written to the
   data log; the caller's header never travels; a reply that echoes the key has it replaced (and any other known value?).
   Check `/proc/<pid>/cmdline` and `environ` of a running relay you start.
5. **The upstream and the network.** One fixed URL; loopback bind only; TLS verified; proxy use; timeouts; a hung
   upstream (does a caller wait past the plugin's own budget, and what does the plugin then do? read its hook).
6. **The gap and concurrency.** The plugin sends its batches at once (`src/output.ts`, `Promise.allSettled`): measure
   the waits for 12 concurrent requests at the 1.05 s gap, and the counts and the log under concurrency.
7. **The data log.** Scrubbed only (the owner wants it as training data: are the rows complete enough to pair a state
   and its questions with the answers?), modes, growth per request, the day boundary.
8. **Fail-closed on every refusal, fail-open for the model.** Read the plugin's hook: on each relay refusal and error
   status, what does the model see (the original output, unpruned)? Anything that makes the plugin retry the relay in a
   loop, or fall back to its default endpoint?
9. **The switch-on plan.** Where `pluginConfigs` must go for this plugin to read it (read the plugin's code and README),
   what else it needs (`CLAUDE_CODE_ENABLE_FUNCTION_HOOKS`), and what the pruner's archive under the project's `.claude/`
   does to the repo's vendored-manifest check (task #370).
10. **Mutation.** Re-run the landing's ten mutants (its message names them) on the final bytes, the control first
   (AF-AP-223), then write your own for the clauses no mutant covers, and report killed and survived with the killing
   test for each.

## Rules

- Work in a clean detached worktree under your own scratch dir at the PIN
  (`git -c core.hooksPath=/dev/null worktree add -q --detach <W> <PIN>`), and remove it at the end. No git write in the
  shared tree; no outward action, no PC bridge, no subagent.
- NEVER switch the relay on: never touch `/root/.claude/settings.json`, `/home/user/.claude/settings.json`, the repo's
  `.claude/`, or the installed plugin, and never start a relay on port 47430. Start test relays on other loopback ports
  and stop each before you report.
- NEVER send anything to codiv.ai or any other outside host: every upstream is a fake on the loopback. Never read
  `/root/.codiv/api.env`, `.pc-bridge.env`, any `*.env` or key file: a secret in a test is a fake built at run time,
  and the relay under test gets `--no-default-sources` with a fake key file, or default sources you have first pointed
  at fakes in a scratch copy.
- In any real transcript, read only `tool_use` inputs and record types, never a `thinking` block, and print only counts,
  bytes and ids.
- `--basetemp` as a pytest ARGUMENT outside any work tree; a long gate in ONE foreground call; counts pasted from
  `scripts/test_summary.sh` with their set ids; stamps from `date -u`; commits cited by origin id or subject.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.

## Report

Every observation with no severity filter; then the blocking predicate (D-034: only a CORE-BLOCKING finding re-opens the
build; here any request shape that sends a secret in a class the relay claims to take, the key leaving by any path, or
a refusal that still sends counts as core-blocking); then a gate recommendation (MERGE-READY /
MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID); and a separate list of what must hold before the switch-on.

## PREMISE — MEASURED at authoring

(printed by `bash scripts/premise_block.sh` at the PIN, added at dispatch)
