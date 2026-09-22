<!-- Evidence lane report (Opus 5 evidence-gatherer), 2026-09-22, extracted verbatim from the lane transcript; file:line anchors refer to the cloned repositories at their audited heads -->

EVIDENCE REPORT — jev-pruner (tamaratran/jev-pruner), pkg `fast-jev-output` 0.1.0, MIT, head 47d017c

Read at `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/jev/jev-pruner`. **Dating caveat:** the clone is shallow (`git rev-parse --is-shallow-repository` = true; 1 commit; head 2026-09-19 10:18:30 +0000). Every file's `git log -1` returns 2026-09-19 — per-file chronology is UNAVAILABLE, not "all changed that day".

## 1. Plugin surface (Claude Code)

| # | Fact | Anchor | Grade |
|---|---|---|---|
|1.1|Manifest `name` `fast-jev-output`, v0.1.0, MIT; `userConfig` block only — no `hooks` key|`.claude-plugin/plugin.json:1-73`|SOLID|
|1.2|Hook registry is `{ "modules": ["./fast-jev-output.ts"] }` — a TS *function-hook module*, not a command hook|`hooks/hooks.json:1`|SOLID|
|1.3|Exactly ONE registration: `on('tool.call', { tool: 'Bash' }, …)`. No other `on(` in the file|`hooks/fast-jev-output.ts:150`|SOLID|
|1.4|Contract: wraps `next(event)` → `answer`; reads `answer.deny`, `answer.isError`, `answer.result`, `answer.text`; returns either the untouched `answer` or `{ result }`|`hooks/…ts:151,162,166,204,269`|SOLID|
|1.5|Event fields used: `event.command`, `event.tool_use_id`|`hooks/…ts:168,183,195,278`|SOLID|
|1.6|Result fields used: `record.stdout`, `.stderr`, `.persistedOutputPath`; on publish deletes `persistedOutputPath`+`persistedOutputSize` and blanks `stderr` when persisted|`hooks/…ts:163,171,174,184,264-267`|SOLID|
|1.7|Host `$` surface required: `$.fs.read/.exists/.write`, `$.env.get`, `$.settings.read`, `$.session.messages()`, `$.http.fetch`, `$.ui.log`, `$.ui.toast`|`hooks/…ts:174,186,190,215-216,233,257,260`|SOLID|
|1.8|Archive dir constant `.claude/fast-jev-output`; file `bash-<tool_use_id ?? Date.now()>.txt`|`hooks/…ts:18,195`|SOLID|
|1.9|Self-gitignore: writes `*\n` to `.claude/fast-jev-output/.gitignore` if absent, before the output file. Repo `.gitignore` also lists the dir|`hooks/…ts:214-215`; `.gitignore:5`|SOLID|
|1.10|Archive is written LAZILY, immediately before the first Jev fetch (`archived ??= saveOutput()`), not after|`hooks/…ts:211-217,229-231`|SOLID|
|1.11|Archived bytes = `combined` (stdout + `\n` + stderr) when not persisted; the SCORED text is `output` (stdout only). Persisted case reuses Claude's file, no new write|`hooks/…ts:174,184,213,216`|SOLID|
|1.12|Secret-looking command/output ⇒ `path = undefined` ⇒ no archive; content is still sent to Jev|`hooks/…ts:192-195`; `README.md:541-544`|SOLID|
|1.13|Re-entry guard: a Bash command whose text contains a previously-pruned archive path is passed through (`archives` Set, per hook instance)|`hooks/…ts:148,168,255`|SOLID|
|1.14|Failure posture: whole body in `try`, `catch` logs `bash output trim skipped (stage=…)` and returns the original answer|`hooks/…ts:165,270-273`|SOLID|
|1.15|Install: `claude plugin marketplace add tamaratran/jev-pruner` + `claude plugin install fast-jev-output@fast-jev-output`; requires `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1`; local alt `claude --plugin-dir .`; types generated from Claude Code 2.1.274|`README.md:413,432-433,453,425`|SOLID|

## 2. Codex variant — what differs

| # | Fact | Anchor | Grade |
|---|---|---|---|
|2.1|Separate manifest `jev-pruner` with `skills` + `hooks` keys|`.codex-plugin/plugin.json:1-7`|SOLID|
|2.2|Hook is a **command** `PreToolUse` matcher on `Bash`: `node "${PLUGIN_ROOT}/dist/codex/hook.js"`, `timeout: 5`|`codex/hooks.json:3-13`|SOLID|
|2.3|That hook does NOT prune. It reads the event from stdin, persists `{sessionId, transcript}` and prints `{}`|`src/codex/hook.ts:1-10`; `src/codex/context.ts:12-24`|SOLID|
|2.4|Pruning is opt-in via a SKILL telling the model to wrap commands: `node "<plugin-root>/dist/codex/run.js" -- npm test`|`codex/skills/jev-pruner/SKILL.md:12-14`|SOLID|
|2.5|`run.js` spawns the child, buffers stdout to 8 MiB (streams through beyond that, skipping pruning), forwards stderr unchanged, preserves exit code/signal; prunes only when `code === 0 && !signal`|`src/codex/run.ts:10-12,27-37,44-54`|SOLID|
|2.6|Session identity from `process.env.CODEX_THREAD_ID`; key from `process.env.TYPESAFE_API_KEY` (no settings/EVAL fallback)|`src/codex/run.ts:50-51`|SOLID|
|2.7|Context cache `~/.cache/jev-pruner/codex/<sessionId>.json`, dir 0700, file 0600, atomic write+rename, session-id charset validated|`src/codex/context.ts:7-23`|SOLID|
|2.8|Archive `<cwd>/.jev-pruner/codex-<uuid>.txt` (0600), dir 0700, `.gitignore` `*`|`src/codex/prune.ts:33-39`; `.gitignore:4`|SOLID|
|2.9|Transcript parsed from Codex JSONL: `session_meta`, `response_item` with `message`/`function_call`/`custom_tool_call`/`*_output`; reasoning skipped|`src/codex/history.ts:10-67`|SOLID|
|2.10|Codex path has a 30 s `AbortController` timeout + abort-signal plumbing; the Claude path has none in plugin code|`src/codex/prune.ts:49-63` vs `hooks/…ts:233`|SOLID|
|2.11|Shares `trimOutput`, `looksSecret`, `exceedsOutputThreshold`, `buildJevRequest`, `parseJevResponse` with the Claude path|`src/codex/prune.ts:4-9,41-42`|SOLID|

## 3. Jev client (src/jev.ts)

| # | Fact | Anchor | Grade |
|---|---|---|---|
|3.1|Endpoint constant `https://api.typesafe.ai/v1/systemone`; default model `jev-latest`|`src/jev.ts:1-2`|SOLID|
|3.2|`buildJevRequest` takes optional `baseUrl`, used as `params.baseUrl ?? SYSTEM_ONE_URL`|`src/jev.ts:79,85`|SOLID|
|3.3|**No caller passes `baseUrl`**: Claude hook passes `{apiKey, model}`; Codex passes `{apiKey}`. No env var, no plugin option, no settings key anywhere (`grep baseUrl/BASE_URL` repo-wide finds only these + `tsconfig.hooks.json:12`)|`hooks/…ts:98`; `src/codex/prune.ts:48`|SOLID|
|3.4|**Endpoint is therefore NOT configurable to a non-TypeSafe server without editing source** (or intercepting `$.http.fetch` / global fetch). Only the `model` string is configurable|derived from 3.2+3.3|SOLID|
|3.5|Request: `POST`, headers `authorization: Bearer <key>`, `content-type: application/json`; body `JSON.stringify({ model, state, questions })`|`src/jev.ts:84-96`|SOLID|
|3.6|`state` as built = `{ context, category?, categoryGuidance?, task, history, command, diagnosticsAndResults, chunks:[{id,text}] }`. README §4 names only `{context, task, history, command, chunks}` — `diagnosticsAndResults` is present in code, unnamed there|`src/output.ts:192-202`; `README.md:29`|SOLID (discrepancy recorded, both sides)|
|3.7|`questions` = `{ [chunkId]: { type:'noul', instructions, criteria:{true,false} } }`, one per chunk, merged per batch|`src/output.ts:205-216,422`|SOLID|
|3.8|**A non-TypeSafe server must return**: HTTP 2xx (`ok`), valid JSON, a non-null object with a non-null object `answers`; for each asked id, `answers[id].noul` a finite number. `model`/`usage` optional and unread by the pruner|`src/jev.ts:100-141`|SOLID|
|3.9|Non-2xx ⇒ `Error("Jev request failed (<status>): <body[0:200]>")`; bad JSON ⇒ `"Jev returned malformed JSON"`; missing answers ⇒ `"Jev response is missing answers"`; bad noul ⇒ `"Invalid Jev answer for <id>"`|`src/jev.ts:106,112,121,138`|SOLID|
|3.10|Batching cap: `MAX_REQUEST_TOKENS = 30_000`; per-request question budget = `30_000 − stateTokens`; a single question exceeding it throws|`src/output.ts:11,222,233-237`|SOLID|
|3.11|Retry: ONLY on an error message containing `max_tokens_exceeded`; ≤2 retries, each halving `maxStateTokens` (floor 2 000) and re-partitioning; budget must remain. No retry for 5xx/429/network|`src/output.ts:365-367,435-443,674`|SOLID|
|3.12|Requests within one attempt run via `Promise.allSettled` but the first rejection is rethrown|`src/output.ts:421-426`|SOLID|
|3.13|Token estimate is a hand-rolled heuristic (letters/6, digits×0.5, symbols 0.9), documented as 2–18% above true count|`src/jev.ts:143-162`|SOLID|

## 4. Pruning algorithm as coded

| # | Fact | Anchor | Grade |
|---|---|---|---|
|4.1|Floor `MIN_OUTPUT_TOKENS = 10_000`; gate is `estimateTokens(output) > max(10_000, minTokens)` — strict `>`, and `minTokens` cannot lower it (also clamped at config resolve)|`src/output.ts:7,81-83`; `hooks/…ts:76`|SOLID|
|4.2|Chunking: lines >2 000 chars split first (`MAX_LINE_CHARS`), grouped by `chunkLines` (default 20) or toward `chunkChars`; groups merged so count ≤ `MAX_CHUNKS = 200`|`src/output.ts:13-14,139-183,392-394`|SOLID|
|4.3|≤2 chunks ⇒ `few_chunks`, untrimmed|`src/output.ts:395`|SOLID|
|4.4|Binary guard: NUL byte, or >5% control chars in first 4 000|`src/output.ts:86-95`|SOLID|
|4.5|Whole-document guard `looksStructured`: parseable JSON object/array, `<?xml`/`<!DOCTYPE`/`---\n` head, XML-ish root tag, `diff --git`/`--- `/`@@ `; commands `cat|bat|jq|yq|diff|git diff|git show|base64|openssl` (leading or after a pipe)|`src/output.ts:102-117`|SOLID|
|4.6|`classifyOutput` ⇒ `document` also when `classifyInformation === 'reference'`; `search` for rg/grep/egrep/fgrep/find/fd/head/tail/sed/git grep; `build` for make/ninja/pytest/jest/vitest/ctest/mvn/gradle(w), npm/pnpm/yarn/bun build·test·lint·typecheck·check·install·ci·add, cargo/go build·test·check·clippy·install, `cmake --build`, pip/uv pip install, `python -m pytest|unittest|build|pip install`|`src/output.ts:126-137`|SOLID|
|4.7|Reference (never scored) regexes: markdown headings/fences, YAML front matter, setext headings, `Help on class/function/module`, Parameters/Returns/Examples, function/class/def, const/let/var, import/from-import, `#include`, C-style signatures, hex-address disassembly, `<symbol>:` label lines|`src/retention.ts:3-16,45`|SOLID|
|4.8|Protected-line set (`isProtectedLine`) = DIAGNOSTIC ∪ RESULT ∪ PYTEST_RESULT. Diagnostics: ERROR/FATAL/FAILED/FAILURE/PANIC/WARN/WARNING, `error:`-family, `error TS\d+`, `^E `, failed/cannot/could not/unable to/denied/refused/timed out, `*Error(`/`*Exception:`, Traceback, `at …:<line>`, vulnerabilit(y|ies), CrashLoopBackOff/OOMKilled, HTTP 4xx/5xx|`src/retention.ts:18-34,39-41`|SOLID|
|4.9|Results: `Test Suites|Tests|Snapshots|Coverage|Results|Summary|Exit code|Exit status:`, Build/Compilation/Tests succeeded/completed/finished/passed/failed, Artifact/Output file/Report/Coverage report path|`src/retention.ts:33`|SOLID|
|4.10|**Keep rule** `keepScore(score, t) = score >= t || score > 0.1` — with default `t=0.5`, a chunk is dropped only when `score <= 0.1`|`src/retention.ts:37,54-56`|SOLID|
|4.11|A chunk is kept if: unscored/incomplete coverage, index 0, index last, itself protected, previous chunk's LAST line protected, next chunk's FIRST line protected, or `keepScore`|`src/output.ts:477-489`|SOLID|
|4.12|Within-chunk refinement (`shrinkChunkWithJev`): 1-line groups when the chunk exceeds its char share, else 5-line groups; needs full history coverage and ≤ remaining budget else returns undefined (chunk preserved)|`src/output.ts:594,603-642`|SOLID|
|4.13|Protected lines keep index−1…index+1 context; boundary lines pinned|`src/output.ts:265-285`|SOLID|
|4.14|Markers — compact mode: header `[fast-jev-output trimmed; retained lines verbatim; omissions marked]`, runs as `[N lines omitted]`, one footer `[fast-jev-output full output: <path> (Read or grep it if needed)]` or `[… not saved to disk; re-run …]`. Non-compact: `[fast-jev-output trimmed N lines (M chars); full output: …]` and `[fast-jev-output trimmed N more lines from this section]`|`src/output.ts:15,252-263,565,578,652-654`|SOLID|
|4.15|Terminal decisions enumerated: `below_threshold, binary, document, few_chunks, no_scoring_capacity, budget_unfit, incomplete_coverage, kept_all, pruned`|`src/output.ts:24-25`|SOLID|
|4.16|Budget pre-check: `minimumRetainedChars` (protected + context + boundaries + fixed metadata) > `maxChars` ⇒ `budget_unfit` BEFORE any Jev call|`src/output.ts:287-306,396-399`|SOLID|
|4.17|Secrets (`src/secrets.ts`, 8 lines): command regex `printenv|env|.env|secret(s)|credential(s)|password|token|keychain|netrc|id_rsa|private_key`; output regex PEM private key, `aws_secret_access_key|api_key|access_token|client_secret|password =/:`, `://user:pass@`. Effect is archive suppression only|`src/secrets.ts:1-8`; `hooks/…ts:192-195`|SOLID|
|4.18|History: split into segments under a token budget, oversized fields binary-searched into `part{field,offset,total_chars}` continuations, surrogate-pair safe; a chunk is fully scored only after every segment votes|`src/history.ts:75-145`; `src/output.ts:403-406,430-431`|SOLID|
|4.19|`goalFromMessages`: last 3 user messages with no tool results, each truncated to 500 chars|`hooks/…ts:109-120`|SOLID|
|4.20|`src/index.ts` exports `trimOutput` + jev module + types (public library surface)|`src/index.ts:1-9`|SOLID|

## 5. Configuration (complete set)

All read from `PluginOptions` (Claude settings `pluginConfigs` / `/plugin configure`), never from env, except the API key.

| Setting | Default | Read at | Grade |
|---|---|---|---|
|`apiKey`|unset|`hooks/…ts:82-83`|SOLID|
|`minTokens`|10 000 (clamped `max(10_000, …)`)|`hooks/…ts:76`|SOLID|
|`persistedOutputs`|true|`hooks/…ts:77-78`|SOLID|
|`persistedMaxChars`|8 000 (0 ⇒ Infinity, then capped by `answer.text.length`)|`hooks/…ts:79,198-203`|SOLID|
|`chunkLines`|20|`hooks/…ts:73`|SOLID|
|`chunkChars`|0 (only set when >0)|`hooks/…ts:84-85`|SOLID|
|`diagnostics`|false|`hooks/…ts:86,275-294`|SOLID|
|`keepThreshold`|0.5|`hooks/…ts:74`|SOLID|
|`maxStateTokens`|25 000|`hooks/…ts:75`|SOLID|
|`maxScoringRequests`|11 (hook) / 40 (library default)|`hooks/…ts:19,87-91`; `src/output.ts:595`|SOLID|
|`model`|`jev-latest`|`hooks/…ts:80`; `src/jev.ts:2`|SOLID|
|Derived request cap|`min(1+maxScoringRequests, max(1, ceil(visibleChars/192)))`, `VISIBLE_CHARS_PER_REQUEST=192`|`hooks/…ts:20,205-208,247`|SOLID|
|API key order|option → `TYPESAFE_API_KEY` → `EVAL_TYPESAFE_API_KEY` → `settings.env.TYPESAFE_API_KEY`|`hooks/…ts:122-144`|SOLID|
|Codex-only env|`CODEX_THREAD_ID`, `TYPESAFE_API_KEY`; `JEV_CODEX_PLUGIN_ROOT`/`JEV_CODEX_MODEL` are TEST-harness only|`src/codex/run.ts:50-51`; `tests/codex-long-session.mjs:15,19`|SOLID|
|Other env (docs/tests only)|`JEV_EVAL_DIAGNOSTICS`, `JEV_LONG_SESSION_{TURNS,BUDGET_USD,DIR}`, `JEV_CODEX_STAGES`, `RUNS`, `REAL_DIR`|`evals/README.md:30`; `README.md:355,571,589-590`|SOLID|
|Removed|`minChars` no longer used|`README.md:526`|SOLID|

## 6. Tests and evals

| # | Fact | Anchor | Grade |
|---|---|---|---|
|6.1|20 vitest files, 114 `it`/`test` call sites (several are `it.each`, so executed cases are more)|`tests/*.test.ts|.mjs` (counted)|SOLID|
|6.2|Coverage by file: output 27, hook-state 18, codex 11, history 9, output-regressions 9, hook 8, codex-boundaries 5, scoring-efficiency 5, token-gate 4, retention 3, codex-session-utils 3, compaction-boundaries 3, compaction-context 3, command-categories 2, compact-markers 2, compaction 2, decisions/partial-chunks/request-ordering/eval-observer parameterized|as listed|SOLID|
|6.3|Offline suite needs no key: `npm test` (vitest), `npm run typecheck`, `npm run build`|`package.json:22-23,31`|SOLID|
|6.4|Key-requiring scripts (hard `assert` on `TYPESAFE_API_KEY`): `test:live` (`tests/jev-live.ts:12-13`), `test:long-session` (`claude-long-session.ts:76`), `test:archive-recovery` (`claude-archive-recovery.ts:31`), `test:codex-session` (`codex-long-session.mjs:21`), `test:codex-real` (`codex-real-tasks.mjs:19`), `eval:manual`/`eval:real`/`eval:accuracy` (`evals/manual/accuracy.mts:9-10`)|as listed|SOLID|
|6.5|`test:long-session` and `test:archive-recovery` additionally spend Claude API budget ($10 / $2 caps)|`README.md:565,578`|SOLID|
|6.6|Accuracy eval: 12 synthetic shapes × 3 needle positions + 1 pass-through case. Ground truth = a planted `needle` line with a `key` substring; scored by `r.output.includes(key)` — a deterministic substring oracle, no LLM judge. Reports needle retention, mean % reduction, wrongly-trimmed pass-through count|`evals/manual/accuracy.mts:24-96` (oracle at :79)|SOLID|
|6.7|Documented sweep numbers (2026-09-18, `jev-latest`): standard 12-scenario 8/8, 83% mean reduction, 0/12 wrongly trimmed, 240 ms mean latency; accuracy 36/36, 87%; real captures 10/10, 54%; needle matrix 9/9|`evals/README.md:233-240,267-274`|SOLID (author-reported; no raw artifact in repo)|
|6.8|The FIVE `claude plugin eval` cases (`all-noise`, `needle-detail`, `needle-error`, `structured-json`, `summary-line`) are graded by an **LLM grader** (`type: llm`) plus a regex trace indicator|`evals/*/graders/criteria.md:1-3`; `…/pruned.md:1-7`|SOLID|
|6.9|**Only committed run artifacts**: three runs, all `caseFilter: needle-error`, Claude 2.1.277, 2026-09-18, ~$0.222 each, `casesTotal 1, casesPassed 0, overallScore 0.5, overallPassRate 0`|`evals/results/2026-09-18T20-40-15-076Z/aggregate-result.json:102-105` (+ the two sibling dirs)|SOLID|
|6.10|The repo states WHY those score 0: an eval run disables non-essential network, `$.http.fetch` to Jev is refused, the hook falls back to the original output and the `pruned` indicator fails — "the suite cannot exercise pruning"|`evals/README.md:196-215`|SOLID|
|6.11|Historical caveat: plugin+manual evals predate the 10 000-token floor|`evals/README.md:171-173`|SOLID|
|6.12|Terminal-Bench pilot via Harbor 0.22.0 (Linux+Docker+claude-sonnet-5), plus Modal budget audit; python harness `evals/{full,process,summarize,harbor_agent,modal_budget}.py` with 14 `evals/test_*.py`|`evals/README.md:282-298`; `evals/*.py`|SOLID|
|6.13|Eval observer is a second pass-through plugin hooking `session.start`, `http.fetch`, `ui.log`, `fs.write`, `tool.call`, writing evidence to `/logs/agent/jev`|`evals/observer/hooks/observer.ts:3-51`|SOLID|

## 7. Dependencies and build

| # | Fact | Anchor | Grade |
|---|---|---|---|
|7.1|**Zero runtime dependencies** — `package.json` has no `dependencies` key; lock confirms `deps: None`|`package.json:1-43`; `package-lock.json` root pkg|SOLID|
|7.2|devDeps: `@types/node ^22.10.2`, `tsx ^4.19.2`, `typescript ^5.7.2`, `vitest ^2.1.8` (123 lock entries transitively, mostly esbuild platform binaries)|`package.json:37-42`|SOLID|
|7.3|Node floor `>=18`; ESM (`"type": "module"`)|`package.json:5,7-9`|SOLID|
|7.4|Build = `tsc` (`tsconfig.json`: ES2022/NodeNext, strict, declaration, `rootDir src` → `outDir dist`, `noEmitOnError`). Hooks typechecked separately under `tsconfig.hooks.json` (noEmit, `types: []`, path alias `claude-code` → `types/claude-code.d.ts`)|`tsconfig.json:1-17`; `tsconfig.hooks.json:1-18`|SOLID|
|7.5|**`dist/` is NOT present** (and gitignored); `node_modules/` absent. The Codex SKILL requires `dist/codex/run.js` to exist|`.gitignore:2`; `ls`; `codex/skills/jev-pruner/SKILL.md:7`|SOLID|
|7.6|`hooks/*.ts` is shipped as TypeScript and imports `../src/*.js` — the Claude host loads/transpiles it (no build step named for the Claude path)|`hooks/hooks.json:1`; `hooks/…ts:8-14`|SOLID|
|7.7|Vendored `types/claude-code.d.ts` is 11 267 lines, generated by Claude Code 2.1.274|`types/claude-code.d.ts`; `README.md:425`|SOLID|

## 8. Claude-Code-specific assumptions a port would have to replace

| # | Assumption | Anchor | Grade |
|---|---|---|---|
|8.1|Function-hook module loader (`hooks.json` `modules`, exported `register: Register`) and the gated `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` early-access API|`hooks/hooks.json:1`; `hooks/…ts:146`; `README.md:413,424`|SOLID|
|8.2|The `tool.call` **wrapping** event — a post-execution hook that calls `next(event)` and REWRITES the result. A Codex/Hermes `PreToolUse` command hook cannot do this; the repo's own Codex answer was a model-invoked wrapper binary instead|`hooks/…ts:150-151`; `codex/hooks.json:3-13`; `src/codex/run.ts`|SOLID|
|8.3|Tool name literal `'Bash'` as the matcher|`hooks/…ts:150`|SOLID|
|8.4|`answer` envelope shape `{result?, deny?, isError?, text?}`, where `answer.text` is the model-visible preview used as the char budget|`hooks/…ts:153,162,200,204`|SOLID|
|8.5|Bash result schema incl. `persistedOutputPath`/`persistedOutputSize` — the engine's large-output file-preview mechanism the plugin exists to improve|`types/claude-code.d.ts:10741-10777`; `hooks/…ts:171,265-266`|SOLID|
|8.6|`$.session.messages()` returning `SessionMessage {role,text,toolUses,toolResults}` (newest 4 096, main conversation only)|`hooks/…ts:190`; `types/…d.ts:2271-2278,7470`; `README.md:81-83`|SOLID|
|8.7|`$.http.fetch` as the egress (no global `fetch` in the Claude path; also the interception point an eval/observer uses, and the only place a base-URL override could be injected)|`hooks/…ts:233`; `types/…d.ts:2751`|SOLID|
|8.8|`$.fs.read/exists/write` as the filesystem (the Claude path imports NO `node:*` builtin — only `src/codex/*` does)|`hooks/…ts:174,215-216`; grep of `node:` imports|SOLID|
|8.9|`$.env.get` + `$.settings.read()` returning a settings object with an `env` map|`hooks/…ts:131-142`; `types/…d.ts:5369`|SOLID|
|8.10|`$.ui.log` and `$.ui.toast(text, {timeoutMs})` UI channels|`hooks/…ts:257,260`; `types/…d.ts:2079`|SOLID|
|8.11|`PluginOptions = Readonly<Record<string, string|number|boolean|readonly string[]>>` delivered by `/plugin configure` / `pluginConfigs` — configuration arrives ONLY through the harness, never env/file|`types/…d.ts:5369`; `hooks/…ts:147`; `README.md:499-510`|SOLID|
|8.12|`.claude/` project-relative archive path, hardcoded|`hooks/…ts:18`|SOLID|
|8.13|`event.tool_use_id` for archive naming and diagnostics|`hooks/…ts:195,278`|SOLID|
|8.14|Marketplace/plugin identity (`.claude-plugin/marketplace.json`, `claude plugin install …@…`, `claude plugin validate`)|`.claude-plugin/marketplace.json:1-16`; `package.json:32`|SOLID|
|8.15|Portable core: `src/jev.ts`, `src/output.ts`, `src/retention.ts`, `src/history.ts`, `src/secrets.ts` have no harness imports — `trimOutput(input, asker, options)` takes an injectable `JevAsker`, so a port replaces the hook shell, not the algorithm|`src/index.ts:1-9`; `src/jev.ts:62-65`; `src/output.ts:669-675`|SOLID|

UNSURE / not found

- `dist/` and `node_modules/` are absent, so nothing built or executed was observed — every behavioural statement above is read from source, not run.
- Per-file git chronology: UNAVAILABLE (shallow clone, single commit). No claim about when any rule was added.
- `src/output.ts:595` declares the library `DEFAULT_MAX_SCORING_REQUESTS = 40` *below* its use at line 374; correct at runtime by module-init ordering, unverified by execution — UNSURE only as to runtime, SOLID as to text.
- Whether any harness path can override the Jev base URL at runtime (e.g. a host-level `$.http.fetch` rewrite): the plugin exposes no such setting; whether Claude Code itself permits such interception outside the eval observer is NOT determined here.
- The `evals/README.md` sweep numbers (§6.7) have no committed raw artifact in the repo — author-reported, unreproduced.
- No CI configuration (`.github/`) exists in the tree, so no independent record of a green suite.
- `demo/JevPrunerDemo/` (Swift, 448 lines) was not read — outside the brief.
- README §1 lists the Jev `state` keys without `diagnosticsAndResults`; whether that is a doc lag or intent is not determinable from the tree.
