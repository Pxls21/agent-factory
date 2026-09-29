# VERIFY-JEV-RELAY: attack the scrubbing relay before the output pruner is pointed at it (task #373, D-109)

Written 2026-09-29 from 12:1xZ (clock read at 12:19:29Z) by the coordinator. Role: sandbox `adversarial-verifier`, model
opus. Do NOT spawn subagents. Return the WHOLE report as your final message (a report-file write is refused for
subagents).

PIN: 3f88707 (origin `claude/soundbox-kit-migration-iz1jwf`).

The change under test: `scripts/jev_relay.py` and `tests/test_jev_relay.py`, landed GATED-PENDING-VERIFY and INERT
(nothing points at the relay; it is not running). The messages of its two commits (origin efb19d8, the landing; 164bf49,
a non-finite `--min-gap` refused) are the builder's account: every claim a hypothesis. The rulings: D-078 (codiv.ai is allowed for this work only after `transcript_export`'s scrubber) and D-109
(the owner: "just build the scrubber"), both in `docs/08_DECISION_LOG.md`.

Why it matters: once switched on, the installed output-pruner plugin (`fast-jev-output@fast-jev-output` 0.1.0, root
`/root/.claude/plugins/cache/fast-jev-output/fast-jev-output/0.1.0/`, READ only, never modify; every plugin path below is
under that root) sends every Bash output over its token
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
10. **Mutation.** Re-run the landing's ten mutants (efb19d8's message names them; the coordinator's driver,
   `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/mut373/mutdrv.py`, is a reference to READ, never a result to trust) on the final bytes, the control first
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

## PREMISE — MEASURED at authoring (2026-09-29 12:5xZ, a clean detached worktree @3f88707)

Printed by `bash scripts/premise_block.sh` from that worktree's root; re-run each `$` line there.

```
$ git rev-parse --short=7 HEAD
3f88707
$ git log --format='%h %s' -2 -- scripts/jev_relay.py tests/test_jev_relay.py
164bf49 jev_relay: a non-finite --min-gap is refused; the relay's verify brief drafted
efb19d8 D-109 recorded; task #373 landed (12:1xZ, GATED-PENDING-VERIFY, INERT): the scrubbing relay between the output pruner and codiv.ai
$ sha256sum scripts/jev_relay.py tests/test_jev_relay.py scripts/transcript_export.py
0aeda61c024b742742c555fdc60b78216b84dac17e377690a7e47879ff21c76d  scripts/jev_relay.py
9b44a0ae598a51686efee590fe520f0425805cbd061d9f889f6c830a17c64ff5  tests/test_jev_relay.py
6ad316dccfca01474c7da0f716e4788407dd8e4c2699d2368e41ea96e5195f42  scripts/transcript_export.py
$ wc -l scripts/jev_relay.py tests/test_jev_relay.py
  330 scripts/jev_relay.py
  377 tests/test_jev_relay.py
  707 total
$ grep -n -E '^(DEFAULT_ENV_FILE|DEFAULT_PORT|MODEL|MODELS|MIN_GAP|MAX_BODY|UPSTREAM_TIMEOUT|USER_AGENT) *=' scripts/jev_relay.py
54:DEFAULT_ENV_FILE = "/root/.codiv/api.env"
55:DEFAULT_PORT = 47430
56:MODEL = "openjev-latest"
57:MODELS = (MODEL,)
58:MIN_GAP = 1.05
59:MAX_BODY = 4 * 1024 * 1024
60:UPSTREAM_TIMEOUT = 120
61:USER_AGENT = "python-httpx/0.28.1"          # the header the proven client sends (openjev_j2.py)
$ grep -n 'KNOWN_VALUE_SOURCES *=' scripts/transcript_export.py
273:KNOWN_VALUE_SOURCES = (
$ bash scripts/pc_suite.sh set-id -- tests/test_jev_relay.py
1 files set=27cdda9dfd9c
$ rm -rf /tmp/premise-jevrelay && mkdir -p /tmp/premise-jevrelay && bash scripts/test_summary.sh tests/test_jev_relay.py --basetemp=/tmp/premise-jevrelay/bt | grep '^pytest-summary:' | sed -E 's/ in [0-9.]+s.*//'
pytest-summary: 24 passed
$ sha256sum /root/.claude/plugins/cache/fast-jev-output/fast-jev-output/0.1.0/src/output.ts /root/.claude/plugins/cache/fast-jev-output/fast-jev-output/0.1.0/src/jev.ts /root/.claude/plugins/cache/fast-jev-output/fast-jev-output/0.1.0/src/secrets.ts /root/.claude/plugins/cache/fast-jev-output/fast-jev-output/0.1.0/hooks/fast-jev-output.ts
6bcc3c1284d335c760cd77f66d39528412f1957b170b6ec2ab218be0d44a2169  /root/.claude/plugins/cache/fast-jev-output/fast-jev-output/0.1.0/src/output.ts
76138fc330264e8237d86365fa32fc3674a0197fc3b173b2f202cb755c2b21bd  /root/.claude/plugins/cache/fast-jev-output/fast-jev-output/0.1.0/src/jev.ts
60a3ef9f072496a95e9f4e6ddb83ac9ebc1c7b5d378f56ec58da25a97a243dfa  /root/.claude/plugins/cache/fast-jev-output/fast-jev-output/0.1.0/src/secrets.ts
8797e97d76d9c8507527809a59cb8e45cf6daca99167381f3ab2612301c1d58f  /root/.claude/plugins/cache/fast-jev-output/fast-jev-output/0.1.0/hooks/fast-jev-output.ts
$ ss -ltn | grep -c ':47430 '
0
[rc=1]
```
