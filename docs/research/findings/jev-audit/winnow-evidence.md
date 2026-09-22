<!-- Evidence lane report (Opus 5 evidence-gatherer), 2026-09-22, extracted verbatim from the lane transcript; file:line anchors refer to the cloned repositories at their audited heads -->

# winnow — evidence report (read-only, no writes/installs/network)

**Root** = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/jev/winnow` — all paths below are relative to it. **Git: ONE commit**, `51d80b9` 2026-09-18 (`git rev-list --count HEAD` = 1) — every file carries that same date; the clone has no history, so per-file git dates carry no signal. License MIT (`LICENSE:1-21`), version 0.5.0 everywhere.

## 1. Plugin surface

| Item | Evidence | S |
|---|---|---|
| Plugin manifest: name `winnow`, v0.5.0, author Ghaleb Dweikat, MIT; no `hooks`/`mcp` keys — layout is by convention | `.claude-plugin/plugin.json:1-11` | SOLID |
| Repo is its own marketplace; one plugin, `source: "./"` | `.claude-plugin/marketplace.json:9-21` | SOLID |
| Hook registration: `{"modules":["./winnow.ts"], "hooks":{"SessionStart":[...]}}` — the module is declared, not a command hook | `hooks/hooks.json:2-17` | SOLID |
| SessionStart (matcher `startup\|resume`) runs `uv run -q --project "${CLAUDE_PLUGIN_ROOT}/sidecar" python -m winnow serve --ensure`, timeout 600 s, statusMessage "winnow: starting sidecar" | `hooks/hooks.json:4-15` | SOLID |
| Function-hook mechanism: TS module typed against `claude-code` (`EngineInterface, Register, SessionMessage`), exported `register: Register = (on) => …`; needs `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1`, CC ≥ 2.1.260 | `hooks/winnow.ts:12,117`; README:44-50,249 | SOLID |
| `tool.call` wrap, one registration per tool in `TOOLS = ['Read','Bash','Grep']`: `const answer = await next(e)`; skip unless `'result' in answer`; skip if `JSON.stringify(answer.result).length < 1500` | `hooks/winnow.ts:16,18,120-124` | SOLID |
| Sidecar request body: `{hook_event_name:'PostToolUse', source:'function-hook', session_id, cwd, agent_id, tool_name, tool_input (event minus tool/tool_use_id/agentId), tool_response: answer.result, tool_use_id, task:{user_request,assistant_intent}}` POSTed to `http://127.0.0.1:47311/hook/post-tool-use` | `hooks/winnow.ts:118,126-138` | SOLID |
| Response contract: empty 2xx = pass-through; JSON 2xx = `{hookSpecificOutput:{updatedToolOutput\|additionalContext}, systemMessage?}`; `x-winnow` header = `{hidden,blocks,before,after,key}` → toast; non-2xx / throw / non-JSON → pass through with a debug log | `hooks/winnow.ts:24-29,90-109,139-143` | SOLID |
| Task from the LIVE session (`$.session.messages()`), not a transcript file: last user text skipping tool-result turns, last assistant text since; head/tail-trimmed at 1500 chars | `hooks/winnow.ts:19,39-65,127` | SOLID |
| Prompt-time hook: `on('prompt.submit', …)`; floor `text.trim().length < 12`; POST `/hook/user-prompt-submit` `{hook_event_name:'UserPromptSubmit', source, session_id, cwd, prompt}`; result appended as `next({...e, context:[...ctx, extra]})` | `hooks/winnow.ts:147-160` | SOLID |
| `winnow_recall` is an **MCP tool**, not a hook: `.mcp.json` server `winnow` = `uv run -q --project ${CLAUDE_PLUGIN_ROOT}/sidecar python -m winnow mcp`; `MCPServer(name="winnow")` with `@server.tool() winnow_recall(key, start?, end?)` and `winnow_stats()`, stdio transport | `.mcp.json:1-8`; `sidecar/src/winnow/mcp_server.py:7,12,21-22,40-41,46-47`; `cli.py:433-437` | SOLID |
| Sidecar lifecycle: `ThreadingHTTPServer` bound to `127.0.0.1`, port 47311; routes `GET /health`, `POST /shutdown`, `/hook/post-tool-use`, `/hook/user-prompt-submit`; idle-exit after 45 min (30 s reaper); `--ensure` = health-check, stop+replace on version mismatch, `Popen([sys.executable,'-m','winnow','serve','--port',…])` detached (`start_new_session`, or `CREATE_NO_WINDOW` on nt), logs to `~/.winnow/serve.log`, waits ≤ 8 s, silent on stdout | `serve.py:33-35,123-196,199-218,237-270`; `cli.py:392-406` | SOLID |
| Port is duplicated, not shared: TS `PORT = 47311` is a constant; `WINNOW_PORT` is read only by CLI/bench/doctor | `hooks/winnow.ts:15`; `cli.py:134,395`; `bench.py:93`; README:172,272 | SOLID |

## 2. Judge interface (sidecar)

| Item | Evidence | S |
|---|---|---|
| Abstraction: `class Judge(Protocol): name: str; def nouls(state, questions) -> JudgeResult`; `JudgeResult(probabilities: dict[str,float], model, input_tokens, output_tokens, latency_ms)` | `judge.py:24-36` | SOLID |
| Backend 1 `TypeSafeJudge` (`name="typesafe"`): `from typesafe_sdk import RetryPolicy, TypeSafeClient`; `TypeSafeClient(model=model, retry=RetryPolicy(max_retries=1, timeout=t), timeout=t)`; call = `self._client.system_one(state, questions)` | `judge.py:67-83` | SOLID |
| Backend 2 `AdapterJudge` (`name="adapter"`): `SystemOneAdapterClient(structured_outputs=True, llm_answer_mode="probabilities", normalize_probabilities=True, provider=…, model=…)`; **no timeout/retry passed** | `judge.py:86-99` | SOLID |
| Backend 3 `LexicalJudge` (`name="lexical"`, replay-only, keyless): `p = min(0.95, 0.05 + 2.0*overlap)` of task-word overlap; `error_present = 0.0` | `replay.py:382-403,406-415` | SOLID |
| Backend 4 `KeywordJudge` (`name="fake-keyword"`, `winnow demo --fake` only): 0.92 if a keyword is in the block else 0.06; `error_present = 0.02` | `demo.py:52-69,85` | SOLID |
| Test double `FakeJudge` (tests only) | `tests/conftest.py:27-45` | SOLID |
| Response parsing is duck-typed: `response.answers[key].noul` (or dict `["noul"]`), `response.model`, `response.usage.input_tokens/output_tokens`; missing keys silently omitted | `judge.py:39-64` | SOLID |
| **Request shape to Jev** = `{"task":{user_request,assistant_intent}, "tool":{"name",  "input": trimmed}, "blocks":{b001: text, …}}` + `questions = {b001: Noul(instructions, criteria), …, "error_present": Noul(...)}` | `hooks.py:115-119`; `questions.py:93-103` | SOLID |
| Question text as coded (structured, default): *"Would the assistant have to look at `blocks.bNNN` to accomplish `task` correctly?"* / *"Is `blocks.bNNN` needed to accomplish `task`? Judge it against `task` and `tool`."* — the README's "is this block needed…" is a paraphrase | `questions.py:29,46,76` | SOLID |
| **URL, headers, key plumbing: absent from the repo.** `grep https://\|base_url\|api_key` over `sidecar/src/winnow/` returns only `config.py:95` (a display-only credential check). The SDK owns the endpoint and auth; keys reach it via `os.environ` | `config.py:92-98`; `config.py:57-89` | SOLID |
| Parallelism: **one batched call**, N+1 questions in a single `nouls()`. No threads/asyncio anywhere except the HTTP server (`grep ThreadPool\|concurrent.futures\|asyncio` → only `serve.py`). Summarizer calls run in a **serial** for-loop | `hooks.py:143,213-224`; `serve.py:23,45,169,213` | SOLID |
| Timeouts/retries: judge 15 s incl. one retry (typesafe only); summarizer `Anthropic(timeout=20.0, max_retries=1)`; any judge exception → log + pass-through | `config.py:138`; `judge.py:76-77`; `summarize.py:31`; `hooks.py:144-147` | SOLID |
| **Local Laya-style `{state,questions}->{answers}` endpoint by config alone?** No path in this repo: `build_judge` is a closed enum (`off/none/0`, `typesafe`, `adapter`) that raises `ValueError` otherwise; neither client is given a `base_url`. Substitution = one new class + one branch (the Protocol is 2 lines). `WINNOW_ADAPTER_PROVIDER` accepts `openai` (README:166) — whether the adapter SDK honours an OpenAI base-URL env var is not determinable from this repo | `judge.py:107-114,71-78,89-99`; `config.py:139` | SOLID (repo) / UNSURE (SDK internals) |

## 3. Sieve algorithm as coded

| Step | Evidence | S |
|---|---|---|
| Gate order: tool in `WINNOW_TOOLS` → judge built → not excluded → extract → `len(text) >= min_chars` → `len(blocks) >= 2` | `hooks.py:100-111`; pre-check `worth_judging` `hooks.py:70-76` | SOLID |
| Exclusions: Read under any `exclude_paths` (default `WINNOW_HOME`); Bash command matching regex `\bwinnow\b` | `hooks.py:45-67`; `config.py:143-144` | SOLID |
| Block splitting: `block_lines=25`; closes early at a blank line once ≥ half full; if `ceil(total/size) > max_blocks(200)` the size grows; ids `b001…`; join-by-newline round-trips exactly | `chunk.py:22-57`; test `tests/test_chunk.py:8,17,24` | SOLID |
| Judge window: only the prefix of blocks fitting `max_state_chars=120000` is sent; the rest are kept unjudged (no probability → kept) | `hooks.py:85-94,114`; `policy.py:46` | SOLID |
| Thresholds: `p >= keep(0.5)` keep · `drop(0.1) <= p < keep` keep+log uncertain · `p < drop` hide · missing p keep | `policy.py:44-52`; `config.py:146-147` | SOLID |
| Error rule: if `error_present >= keep` → keep everything, reason `error_present` (the error Noul is asked over the whole `blocks` object) | `policy.py:38-39`; `questions.py:15-24`; test `tests/test_policy.py:19` | SOLID |
| Min prune ratio: if pruned chars / all chars < 0.2 → keep everything, reason `below_min_prune_ratio` | `policy.py:54-58`; `config.py:151` | SOLID |
| Stub format (3 lines): `[winnow] Lines {a}-{b} ({n} lines) hidden: judged unlikely to matter for the current task (relevance <= {max_p:.2f}).` / `[winnow] Summary: …` or `[winnow] Hidden content: {digest}` or `[winnow] Summary unavailable.` / `[winnow] Full text cached as key {key}. Call winnow_recall(key="…", start=…, end=…) if you need it.` Hidden blocks are grouped contiguously; one stub per group | `stub.py:47-72,75-88`; `chunk.py:60-68` | SOLID |
| Cache: key = `sha256(session_id \0 tool_use_id \0 text)[:12]`; file `~/.winnow/cache/<key>.json` holding full text, per-block p + hidden flag, task, describe, line_offset; `load()` refuses a non-alnum key; **no TTL at write time** — `winnow clean` drops > 30 days then trims to 200 MB | `cache.py:14-18,21-38,41-89`; `hooks.py:160-180`; README:145,278 | SOLID |
| Summarizer: Anthropic Messages API, default `claude-haiku-4-5`, `max_tokens=300`, fixed system prompt, per hidden group, first `WINNOW_SUMMARY_MAX_GROUPS=4` groups, `[:20000]` chars each; optional (`WINNOW_SUMMARY=0`); rate-limit/status/connection errors → `None` | `summarize.py:10-15,24-54,57-63`; `hooks.py:213-224`; `config.py:152-155` | SOLID |
| Deterministic digest fallback (no model): Grep → "N matching lines in M files: file (n), …"; else "N lines (mostly comments / mostly imports / highly repetitive), starting: <first line ≤70 chars>" | `stub.py:14-44`; tests `tests/test_review.py:116,122,130` | SOLID |
| Tools + shapes: Bash `tool_response["stdout"]`; Read `tool_response["file"]["content"]` with `startLine` as line offset, rebuild updates `numLines`; Grep `tool_response["content"]`; bare-string responses pass as text; anything else → `None` (pass-through) | `extract.py:30-82`; test `tests/test_extract.py:36` | SOLID |
| Size floors: sidecar 1500 chars of **extracted text**; module 1500 chars of **`JSON.stringify(result)`** — two different measures of "large" | `config.py:145`; `hooks.py:106`; `hooks/winnow.ts:18,124` | SOLID |
| Shadow mode: judges, caches, renders a preview and logs `would_rewrite`, returns `None` (no rewrite, no summarizer) | `hooks.py:182-209`; `config.py:163-166`; `tests/test_shadow.py:21` | SOLID |

## 4. Memory-ranking hook

| Item | Evidence | S |
|---|---|---|
| Candidates: `~/.claude/projects/<slug>/memory/*.md` where slug = `re.sub(r"[^A-Za-z0-9]","-", cwd)`, plus every dir in `WINNOW_CONTEXT_DIRS`; `memory.md` (case-insensitive) skipped; front matter `name`/`description` parsed; capped at `context_max_candidates=60` | `memory.py:17,29-35,61-84` | SOLID |
| Ranking: the same judge, one `Noul` per candidate — *"Would the assistant need to read `candidates.<id>` to handle `prompt` well?"*; state = `{prompt: prompt[:4000], candidates:{id:{title,description,excerpt: text[:600]}}}` | `hooks.py:264-282` | SOLID |
| Injection: sort by p, keep `p >= context_gate(0.5)`, take top `context_top_k(3)`, total budget `context_max_chars(8000)`, per-file truncation marker `\n[truncated]`, header line "winnow selected these files as relevant to this prompt (read them here instead of opening them):"; returns `hookSpecificOutput.additionalContext` | `hooks.py:300-327`; `config.py:157-160` | SOLID |
| Floors/short-circuits: prompt < 12 chars, no judge, or no candidates → `None`; shadow logs `would_inject` only | `hooks.py:257-262,306-308` | SOLID |

## 5. Configuration and keys

All `WINNOW_*` defaults are read in one place, `config.py:131-161` (table in README:160-189 matches the code on every row I checked). Additional reads outside that table: `WINNOW_PORT` (`cli.py:134,395`, `bench.py:93`), **`WINNOW_TRANSCRIPTS_ROOT`** (`transcript.py:89`, `replay.py:250`) — undocumented in the README table; `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` (`cli.py:165`); `USERNAME`/`USER` for the reviewer default (`cli.py:329`).

| Item | Evidence | S |
|---|---|---|
| Key handling: `load_env_file()` parses `KEY=VALUE` (optional `export `, quote-stripping, `#` comments) from `$WINNOW_HOME/env`; **environment wins over file**; returns names loaded. Called at every CLI start (`cli.py:383`) and re-read by the sidecar on mtime change (which also drops the runtime so a key/threshold edit takes effect live) | `config.py:53-89`; `serve.py:52-69`; test `tests/test_config.py:6-26` | SOLID |
| Keys named: `TYPESAFE_API_KEY`, `ANTHROPIC_API_KEY` — only ever *reported* by winnow (`set (ts-abc...)` / `not set`, redacted after 6 chars); never passed to a client in repo code | `config.py:92-98`; test `tests/test_config.py:32-38` | SOLID |
| README "add a key": `~/.winnow/env` (Windows `%USERPROFILE%\.winnow\env`) or the `env` block of `~/.claude/settings.json`; `WINNOW_JUDGE=adapter` as the no-Jev path | README:93-112 | SOLID |
| `winnow doctor` prints: version, home, mode, env-file status, both credential statuses, judge+model, tools, thresholds, summary, judge-backend build result, summarizer build result, cache-dir writability, sidecar health, and where the function-hooks flag is set (`settings` / `env` / NOT ENABLED); exit 1 if any of those failed | `cli.py:96-151,154-167` | SOLID |
| CLI surface: `doctor, demo [--fake], stats, recall, replay {extract,judge,score,run,sample,label,import-labels,agreement}, serve [--ensure\|--status\|--stop], bench [--http], clean, mcp, hook <event>, review` | `cli.py:382-440`; README:133 | SOLID |

## 6. Tests and CI

18 Python test files, 0 network/key-dependent: the autouse fixture pins `WINNOW_HOME=tmp`, `WINNOW_JUDGE=off`, `WINNOW_SUMMARY=0`, `WINNOW_MIN_CHARS=10`, **`WINNOW_DROP=0.3`** (explicitly not the shipped 0.1) (`tests/conftest.py:11-19`). No `pytest.mark.skip`, no `requests`/socket use outside the loopback server fixture. Coverage by file: `test_chunk` (round-trip, blank-line break, max-blocks growth) · `test_policy` (drop/keep/error-gate/missing-p/min-ratio) · `test_hooks` (prune+stub, error never pruned, small/unsupported pass-through, judge-failure pass-through, judge-off inert, Read line numbers, prompt injection + gate, JSON-serializable output) · `test_extract` (per-tool shapes, unknown → None) · `test_exclude` (WINNOW_HOME reads, `winnow` commands, custom paths) · `test_serve` (health, fast path, judged rewrite, bad JSON/404, notify-once when the judge can't start, absent server) · `test_function_hook` (task override beats transcript, junk rejection, trimming, slug guess, X-Winnow header, `"source"` recorded) · `test_transcript` (last request/intent, turn reset, subagent transcript, tail reading) · `test_shadow`, `test_review`, `test_replay` (weak labels, window, AUC vs ECE), `test_labels`, `test_config`, `test_clean`, `test_demo`, `test_questions`. TS: `tests/winnow.test.ts:1-77` — `taskFrom` (3 cases), `head`/`tail`, `describeMeta` exact string, and three pass-through cases (sidecar unreachable, small result, denied call); imports `claude-code/testing`.

CI `.github/workflows/tests.yml`: job `test` — matrix ubuntu+windows × Python 3.10/3.13, `pip install uv`, `uv sync`, `uv run pytest -q`, then `uv run winnow demo --fake` with `WINNOW_HOME=$RUNNER_TEMP/winnow` (`:9-29`); job `function-hooks` — node 22, `npm install -g @anthropic-ai/claude-code`, `claude plugin test .` with `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` (`:31-41`). No lint/typecheck job; `tsc` is never run in CI though `tsconfig.json` exists.

## 7. Dependencies

`sidecar/pyproject.toml:5-13,15-16,18-19,25-29`: `requires-python = ">=3.10"`; deps `typesafe-sdk>=0.6.0`, `system-one-adapter[anthropic]`, `anthropic>=1.0`, `mcp>=2.0`; dev `pytest>=8`; hatchling build; console script `winnow = winnow.cli:main`; `testpaths=["tests"]`. `uv.lock` (1299 lines, 48 packages) pins `typesafe-sdk 0.6.0` (deps `httpx2`, `msgspec`, `tenacity`) and `system-one-adapter 0.1.3`, both from PyPI with sha256 hashes (`uv.lock:1133-1145,1225-1233`). uv is the only invocation path in hooks (`hooks/hooks.json:10`, `.mcp.json:5`). TS: only `hooks/winnow.ts` + `tests/winnow.test.ts`; no `package.json`, no `node_modules` committed, no build step — `tsconfig.json:1-17` is `noEmit`, `strict`, `module: esnext`, including `.claude/types` (gitignored, generated by `/plugin-types`), `hooks`, `tests`. Node is used only by Claude Code itself.

## 8. The skill

`skills/winnow/SKILL.md:1-28`. Front matter has exactly two fields: `name: winnow`, `description:` (one long sentence: how to read a stub, "call winnow_recall to restore it", trigger = a result containing `[winnow]` or the tools being available). Body: what winnow is (one paragraph naming Jev / the adapter and the one-question-per-block design); a verbatim stub example; four "how to treat it" rules — (a) the summary is from a cheap model, trust it for orientation not exact values; (b) call `winnow_recall(key, start?, end?)` rather than re-running the command, "recall is cheaper and does not re-trigger side effects"; (c) **"Outputs that show an error are never pruned"**; (d) the line-number caveat — Claude Code renumbers a rewritten Read from 1, so use the stub's range with `Read` offset/limit or recall, and `Edit` is unaffected because it matches text. Closes with the two tool signatures.

## 9. Claude-Code-specific assumptions a Hermes port must replace

| Assumption | Evidence |
|---|---|
| The whole hook mechanism: `claude-code` module types, `register`, `on('tool.call'…)` with `next(e)` → `{result}`, `on('prompt.submit')` with `e.context` | `hooks/winnow.ts:12,117-160` |
| Engine services `$.http.fetch`, `$.ui.log`, `$.ui.toast`, `$.session.id()/.cwd()/.messages()`, and the `SessionMessage` shape (`role`, `text`, `toolResults`) | `hooks/winnow.ts:39-53,81-87,112-114,139-142` |
| The flag + settings path `~/.claude/settings.json` `env.CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` | `cli.py:154-167`; README:46-50 |
| `${CLAUDE_PLUGIN_ROOT}` expansion, plugin `hooks/hooks.json` + `.mcp.json` + `skills/` conventions, `claude plugin install/test/marketplace` | `hooks/hooks.json:10`; `.mcp.json:5`; README:54-87,256 |
| Literal tool names `Read`/`Bash`/`Grep` **and their exact result objects** (`.stdout`; `.file.content/.startLine/.numLines`; `.content/.numLines`) — a rewrite that doesn't match the shape is silently ignored | `extract.py:30-82`; `hooks/winnow.ts:16` |
| Payload keys `tool_name/tool_input/tool_response(or tool_output)/tool_use_id/session_id/cwd/agent_id/agent_type/transcript_path/prompt` and output envelope `hookSpecificOutput.{updatedToolOutput,additionalContext}` + `systemMessage` | `hooks.py:100-130,242-247,322-327`; `cli.py:31-41` |
| Transcript layout: `~/.claude/projects/<cwd-slug>/<session_id>.jsonl`, subagent `<dir>/<session_id>/subagents/agent-<agent_id>.jsonl`, JSONL entry schema (`type`, `message.content[].type == text\|tool_result`, `isMeta`) | `transcript.py:61-90,110-148`; `replay.py:250` |
| Memory layout `~/.claude/projects/<slug>/memory/*.md` with `MEMORY.md` as the already-loaded index | `memory.py:17,33-35`; README:38 |
| MCP tool exposure as the only way Claude reaches `winnow_recall` | `.mcp.json:1-8`; `mcp_server.py:21-22` |
| Claude Code behaviours relied on in prose: Read refuses files > 256 KB (result becomes a short string, so nothing reaches the sidecar); Read output is renumbered from 1 | DESIGN.md:192; SKILL.md:23 |

## 10. docs/ and measured numbers

`docs/DESIGN.md` (273 l) — design rationale, hook mechanics, state engineering, thresholds, replay/label design, measured tables, known limits, 11-item roadmap. **It contains a duplicated block**: §"An open judge? jevlike", §"Latency, measured", §"The resident sidecar", §"Function hooks" appear twice (`:140-194` and `:196-249`), and the two copies disagree — `:185` "changes two things" vs `:241` "changes three things", the second still describing the 0.4.0 dedupe layer and saying "A live session with the flag on had not been run when this was written" (`:247`) while the first reports the 2026-09-18 live run (`:192`). SOLID.
`docs/WRITEUP.md` (79 l) — draft write-up of the same numbers, dated 16 Sep 2026, with caveats and a reproduce script.
`docs/experiments/jevlike_experiment.py` (207 l) — trains jevlike on the replay cases as a keyless local judge, splits by transcript, scores with `winnow.replay.score` (`:1-6`).
`docs/results/2026-09-16/` — 7 JSON score files (in-repo artifacts produced by `winnow replay score`); `docs/results/2026-09-18/` — 3 jevlike run files.

| Number | Where claimed | In-repo artifact? |
|---|---|---|
| ECE Jev 0.1435 (weak) / 0.1776 (hand, default q) vs lexical 0.3147; 300 cases, 1515 blocks, 97 hand-labeled, needed fraction 0.4845 | DESIGN.md:77-87; WRITEUP.md:25-33 | YES — `results/2026-09-16/score-typesafe.json`, `score-typesafe-hand.json`, `score-lexical.json` (keys `ece`, `blocks_scored`, `needed_fraction`) |
| Median judge latency 86 ms (default) / 94 ms (structured) / 103 ms (strict); cost $0.036–$0.045 per 300 cases, 863k–1.07M input tokens at $0.042/M | DESIGN.md:82-83,169; WRITEUP.md:30-31 | YES — same files, `latency_ms_median`, `est_cost_usd_at_jev_price`, `judge_input_tokens`; price constant `log.py:18` |
| At `drop=0.1`, structured, hand labels: 23 hidden blocks, regret **0.0**, hidden precision 1.0, 20.7% of chars hidden in that sample (DESIGN quotes 4.6% population/weak) | DESIGN.md:130-138 | YES — `score-typesafe-structured-hand.json:28-35` |
| Weak-vs-hand agreement 69.1% (40/20/27/10 confusion), per-bin hand needed rates 0.255 / 0.60 / 0.80 | DESIGN.md:111; WRITEUP.md:33 | YES — `results/2026-09-16/agreement.json:6-26` |
| jevlike table: Jev ECE 0.141 AUC 0.701; lexical 0.313/0.635; jevlike byte 0.315/0.453; Qwen2.5-0.5B lr2e-3 0.168/0.566, lr2e-4 0.135/0.497 (195 held-out blocks) | DESIGN.md:144-151 | YES — `results/2026-09-18/*.json` (3 files, keyed by judge name) |
| Latency: interpreter 92 ms · small result `python -m winnow` 274 ms · via `uv run` 374/381 ms · +`import typesafe_sdk` 566 ms · **via sidecar 16 ms** | DESIGN.md:161-181,234-235; README:251,269 | CLAIMED — producer is `winnow bench` (`bench.py:1-45`, `cli.py:388-391`); **no stored bench artifact in the repo**; stated as "on this machine (Windows 11, Python 3.14)" |
| First live function-hook run 2026-09-18: 25 KB README judged in 517 ms, 27 of 28 blocks hidden, `tool.call` settled in 697 ms | DESIGN.md:192 | CLAIMED — no artifact |
| Human review: 7 stubs reviewed, 6/6 genuine fine, every hidden block ≤ 0.10; 20-block human audit 38% agreement with model labels | DESIGN.md:268-269; WRITEUP.md:60-62 | CLAIMED — producer is `winnow review` → `~/.winnow/review.jsonl` (`review.py:1-9,310-329`), outside the repo |
| Cost table "under a cent" / "a few cents" per 10k-token output | README:147-152 | CLAIMED (arithmetic from list prices) |

## UNSURE / not found

- **Jev URL, headers, auth wire format, and whether `TypeSafeClient` accepts a `base_url`** — nothing in the repo; owned by `typesafe-sdk 0.6.0` (PyPI, not vendored). Same for `system-one-adapter 0.1.3` and any OpenAI base-URL override behind `WINNOW_ADAPTER_PROVIDER=openai`.
- Whether a Jev call is internally parallel/batched on the server; only the client-side single call is visible (`judge.py:82`).
- `Noul` semantics/return schema beyond the duck-typed `.noul` float (`judge.py:39-46`).
- Actual cache growth/eviction in practice: no TTL at write, `clean` is manual (`cache.py:21-26,41`); README:145 says "no eviction yet".
- No `bench` result artifact, no live-session decision log, no `review.jsonl` in the repo — the 16 ms / 381 ms / 517 ms / human-regret figures are unreproduced here (no network, no key, nothing run).
- `.claude/types` (referenced by `tsconfig.json:16`) is gitignored and absent, so the TS module does not typecheck from a clean clone without running `/plugin-types` inside Claude Code.
- Whether `hooks.json`'s `modules` key and the SessionStart command coexist correctly on any CC version other than the one CI installs (`@anthropic-ai/claude-code` is unpinned, `tests.yml:38`).
- The repo has ONE squashed commit, so no change history, no authorship trail, and no way to date any claim independently of `51d80b9` (2026-09-18).

