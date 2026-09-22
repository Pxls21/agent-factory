<!-- Coordinator audit (read-only, no install, no network beyond the blob-less clone), 2026-09-22 15:1xZ; file:line anchors refer to the cloned repository at the scratchpad path below. The fifth repository of the Jev/Laya audit (task #104), named by the owner 2026-09-22 14:5xZ: "https://github.com/tamaratran/fast-jev-compaction — I found this aswell". -->

# EVIDENCE — tamaratran/fast-jev-compaction @ e3f262a (MIT)

Clone: `git clone --filter=blob:none --depth 1` at `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/fast-jev-compaction`; head `e3f262a7f4d42bd8dd32ced30d26176f7cb545b0` (2026-09-17 22:29:18 +0000, "Merge pull request #17 … readme-tagline"). **Dating caveat:** the clone is shallow; the head date is the only git date read. 26 tracked files; `LICENSE` = MIT (copyright line "(c) 2025", no name). Same author as `jev-pruner` (`docs/research/findings/jev-audit/jev-pruner-evidence.md`).

## 1. What it is

| # | Fact | Anchor | Grade |
|---|---|---|---|
| 1.1 | An npm library (`src/`, TypeScript, `"type":"module"`, node ≥ 18, **no runtime dependencies** — `package.json` has only `devDependencies`: `@types/node`, `tsx`, `typescript`, `vitest`) | `package.json:1-39` | SOLID |
| 1.2 | AND a Claude Code function-hook plugin: `hooks/hooks.json` = `{"modules":["./fast-jev.ts"]}`; the marketplace is the repo's own `.claude-plugin/marketplace.json` (plugin `fast-jev-compaction`, source `./`, v0.3.0, MIT); `plugin.json` declares nine `userConfig` values (`apiKey` sensitive, `keepThreshold` 0.5, `preserveRecentMessages` 6, `compactAtPercent` 60, `minReductionRatio` 0.25, `maxStateTokens` 25000, `maxRequestTokens` 30000, `truncateHeadChars` 300, `model` `jev-latest`) | `hooks/hooks.json:1`, `.claude-plugin/marketplace.json:1-16`, `.claude-plugin/plugin.json:1-66` | SOLID |
| 1.3 | Purpose: replace the compaction SUMMARY with the original messages minus the tool calls / tool results Jev scores as no longer needed; user and assistant text is never rewritten (README "What and why") | `README.md:1-24` | SOLID |
| 1.4 | Sizes: `src/compact.ts` 309 lines, `src/state.ts` 304, `src/types.ts` 202, `src/request.ts` 80, `src/messages.ts` 13, `src/index.ts` 6, `hooks/fast-jev.ts` 310 (1,267 total) | `wc -l` | SOLID |

## 2. The model call (the seam that matters for D-040 / D-041)

| # | Fact | Anchor | Grade |
|---|---|---|---|
| 2.1 | Endpoint constant `SYSTEM_ONE_URL = 'https://api.typesafe.ai/v1/systemone'`; `buildJevRequest` POSTs `{model, state, questions}` as JSON; `parseJevResponse` accepts only an `answers` object; `noulAnswer` requires a finite numeric `noul` per answer | `src/request.ts:3`, `:14-36`, `:38-64`, `:66-80` | SOLID |
| 2.2 | The key comes from the `apiKey` option or `process.env.TYPESAFE_API_KEY`; a missing key THROWS (`TYPESAFE_API_KEY is not configured`) | `src/client.ts:5-30` | SOLID |
| 2.3 | `baseUrl` is an injectable client option ("Defaults to the System One endpoint") → the request can be pointed at a first-party loopback `/v1/systemone` (the `laya-decide` service of RESEARCH-FINDINGS-2 part 1) without patching the library; the hook adapter passes `$.http.fetch` (Claude Code's fetch) as the transport | `src/client.ts:9-10,19,25`, `hooks/fast-jev.ts:263-270` | SOLID |
| 2.4 | Bring-your-own transport: implement `JevAsker` (`ask(state, questions)`) and call `compact(messages, asker, options)`; the building blocks (`collectToolCalls`, `fitState`, `batchCalls`, `decideCall`, `applyDecisions`) are exported | `README.md` "To bring your own transport"; `src/compact.ts:56,73,101,149,257`; `src/state.ts:62,195` | SOLID |
| 2.5 | Questions: for every non-pinned tool call TWO `noul` questions (keep the CALL; keep the RESULT verbatim); decisions against `keepThreshold`: `keepResult ≥ t` keep both · else `keepCall ≥ t` keep the call and truncate the result to `truncateHeadChars` + a note · else drop the call with its result; a result is never left without its call | `README.md` "How it works" 4-7; `src/compact.ts:56-71,101-147,149-226`; `src/types.ts:57` (`CallAction = keep | drop_result | drop_call`) | SOLID |
| 2.6 | State fitting: the whole conversation oldest-first with tool results replaced by a one-line note, fitted into `maxStateTokens` in stages (inputs truncated 1000→200→60 chars; texts abridged head+tail; old messages collapsed; old calls one-lined; call-less messages dropped; call-only runs folded); tokens ESTIMATED without a tokenizer ("a word per six letters, half a token per digit, ~one per other symbol", calibrated "a little above the counts Jev reports"); if it still does not fit, compaction THROWS; the full state is resent with every request (batches under `maxRequestTokens`, run concurrently) | `README.md` "How it works" 2-5; `src/state.ts:28-38,195-304` | SOLID |

## 3. The Claude Code hook surface

| # | Fact | Anchor | Grade |
|---|---|---|---|
| 3.1 | `register` binds `session.compact`: runs `compactSession(event.messages, …)`, logs a per-call `decisions:` line, and on `reductionRatio < minReductionRatio` OR any thrown error returns `next(event)` (= Claude Code's built-in summary); on success returns `{ messages }` (the pruned verbatim history) with a toast | `hooks/fast-jev.ts:259-290` | SOLID |
| 3.2 | `turn.complete` reads `$.session.usage()` and calls `$.session.compact()` when `context.percent ≥ compactAtPercent` (60), with an in-flight guard | `hooks/fast-jev.ts:292-309` | SOLID |
| 3.3 | Function hooks are EARLY ACCESS: `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` must be set; the checked-in type reference `types/claude-code.d.ts` was generated by Claude Code **2.1.274** (`session.compact` at `:2344-2352`, `:3320-3322`; `turn.complete` at `:288-292`) | `README.md` "Install in Claude Code"; `hooks/README.md` "Scope and caveat"; `types/claude-code.d.ts` | SOLID |
| 3.4 | MEASURED in THIS sandbox 2026-09-22 15:1xZ: `claude --version` = `2.1.278 (Claude Code)`; the installed CLI at `/opt/claude-code/bin/claude` contains the strings `session.compact` (18 hits), `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` (5), `turn.complete` (24) — the surface EXISTS in the sandbox CLI; whether it is enabled/allowed for a CCR session is NOT measured (no run) | `grep -ac` on the binary | SOLID (presence) / UNSURE (activation) |
| 3.5 | Tests: `tests/fast-jev-compaction.test.ts` 23 cases + `tests/hook.test.ts` 6 cases (vitest), "use a fake Jev and never contact TypeSafe"; the demo is the live network check | `tests/*.ts`, `README.md` "Development" | SOLID (counts by `grep -cE '^\s*(it|test)\('`; NOT run here) |
| 3.6 | Repo-declared limits: only tool calls/results are candidates; token sizes are estimates; "a probability is not a proof that a result is safe to delete. The assistant can always re-run the tool"; near the state ceiling it costs one request per handful of questions | `README.md` "Limitations" | SOLID |

## 4. Fit against this project's constraints (facts, not a verdict)

- **Rule 3 / sole egress:** as shipped the plugin calls `api.typesafe.ai` directly from Claude Code with a hosted key — a direct provider credential and a second egress. Pointing `baseUrl` at the first-party loopback `laya-decide` service (D-040, D-041) removes both; nothing in the code pins the host (§2.3). NOT tested here.
- **Rule 12 / no-LLM-judge in the gate spine:** the plugin decides what a CONTEXT keeps, never a gate verdict; the advisory-only invariant of RESEARCH-FINDINGS-2 part 2 applies unchanged.
- **Where it would sit:** the sandbox coordinator session (Claude Code) — it is the only Jev/Laya candidate in the audit that addresses COMPACTION of this session rather than tool-output pruning (jev-pruner) or a decision cache (jevcache); Hermes lanes have no equivalent hook in this repo (`transform_terminal_output` is the tool-result hook, not a compaction hook — measured present in both Hermes trees 2026-09-22).
- **Venue fact:** the sandbox CLI is 2.1.278 ≥ 2.1.274 (§3.4); the early-access flag's effect under CCR is unmeasured.
- **Pinning:** commit `e3f262a` is pinnable (a real git history, MIT) — unlike `jevcache` (D-041); vendoring would enter `upstream.lock.yaml` + the vendored manifest if adopted.
- **NOT done:** no install, no test run, no live Jev call, no measurement of the token estimator against a real transcript, no check of the 2.1.274→2.1.278 hook-type drift.
