<!-- Evidence lane report (EXPLORE lane, evidence-gatherer), 2026-09-23, brief af/tasks/briefs/jev-laya/CANNY-AUDIT-brief.md. STATIC READING ONLY: nothing from the clone was run, built, installed or imported; no network call was made. `canny/<path>:<line>` = the clone at f2c5e53; `af/<path>:<line>` = /home/user/agent-factory as on disk 2026-09-23 (uncommitted files are marked). Facts only: no verdict, no ranking, no recommendation. -->

# EVIDENCE — qkal/canny @ f2c5e53 (package `canny-warden` 0.3.0, MIT)

Clone: `/home/user/qkal/canny`, origin `https://github.com/qkal/canny`, HEAD `f2c5e53779445d60dc4a09d2dbced2308fccb820` (2026-09-23 01:23:49 +0200, author "Qkal", "chore(release): 0.3.0 (#21)"). **Dating caveat:** the clone is shallow (`git rev-parse --is-shallow-repository` = true, 1 commit); every file's `git log -1` returns f2c5e53, so per-file chronology is UNAVAILABLE. The CHANGELOG dates the releases 0.1.0 = 2026-09-18, 0.2.0 = 2026-09-21, 0.3.0 = 2026-09-23 (`canny/CHANGELOG.md:77,38,7`). Sizes (`wc -l`): `src/` 2,039 lines in 9 files (checks 250, cli 274, config 106, events 474, hook 373, install 140, jev 124, ledger 228, rules 70); `dist/` 1,707 lines in 9 files; 13 `test/*.test.ts` files + `setup.ts` + `smoke.sh` + 4 fixture files + 1 snapshot; `bench/run.mjs` 169 lines + 5 task directories.

**Method.** I read in full, with line numbers: every `src/` and `dist/` file, every test file, the fixtures' key sets, `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `package.json`, `tsconfig*.json`, `vitest.config.ts`, both CI workflows, `.githooks/pre-commit`, `bench/run.mjs`, and each bench task's `prompt.txt`, `solution.sh` and `package.json`. Two Python scripts of my own made the static counts. They read the clone as text only: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/canny/cmp.py` (a tokenizer plus a literal and comment diff) and `.../scratchpad/canny/ops.py` (operator counts). No timing was measured. "NOT run" marks every behavioral statement: all of them are read from source.

**af files cited, with their last commit** (`git log -1`, checked 2026-09-23):

| af file | last commit | working tree |
|---|---|---|
| `scripts/laya_systemone_server.py` | 66cb5da 2026-09-22 18:40:02 +0000 | MODIFIED, uncommitted (+94/-29). The contract lines 5-6, 15-16 and the `type` check read the same in HEAD (HEAD:5-6, 15-16, 124-125) |
| `scripts/no_laya_in_gates.py` | 5eae256 2026-09-22 20:34:11 +0000 | clean |
| `seeds/seed-laya-j1-v1.yaml` | 233ee53 2026-09-22 16:50:16 +0000 | clean |
| `tasks/laya-j1-breakdown.md` | 87f9a68 2026-09-22 16:58:39 +0000 | clean |
| `docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md` | ec50851 2026-09-22 16:18:16 +0000 | clean |
| `docs/research/findings/JEV-LAYA-AUDIT-2026-09-22.md` | 2eaf06e 2026-09-22 12:22:24 +0000 | clean |
| `.claude/settings.json` | 3c0d49e 2026-09-02 21:21:05 +0000 | clean |
| `.claude/hooks/turn-retro-gate.sh` | 1e8ecee 2026-09-03 07:28:16 +0000 | clean |
| `harness-ports/bin/hook-shim.sh`, `harness-ports/bin/codex-hook-adapter.py` | 097b0e3 2026-09-03 05:38:59 +0000 | clean |
| `harness-ports/bin/hermes-hook-adapter.py`, `harness-ports/hermes/config-snippet.yaml` | 569914b 2026-09-15 07:52:54 +0000 | clean |
| `harness-ports/tests/test_hermes_hook_adapter.py` | 8ecf41c 2026-09-03 21:19:40 +0000 | clean |
| `todo/BUILD-TASKLIST.md` (line 162 cited; that line is in HEAD) | 879c6f9 2026-09-22 22:01:04 +0000 | MODIFIED elsewhere, uncommitted |
| `tasks/briefs/jev-laya/PCJ1-report.md` | — | UNTRACKED |

## 1. Architecture

### 1a. Module roles

| # | Fact | Anchor | Grade |
|---|---|---|---|
|1.1|`cli.ts`: the entry point (`bin canny` → `dist/cli.js`). A switch over `hook`, `init`, `status`, `sessions`, `replay`, `remove` and `trust`; with no command it prints help|`canny/src/cli.ts:42-83`; `canny/package.json:27-29`|SOLID|
|1.2|`cli.ts hook()`: reads one JSON value from stdin, runs `normalize`, picks the ledger file, and builds the judge. The judge's log appends `type:"jev"` entries to the ledger. It then loads the config, runs `handle` and `serialize`, and writes one JSON object to stdout. Any throw appends a line to `errors.log`, and stdout still gets `{}`|`canny/src/cli.ts:85-99`|SOLID|
|1.3|`events.ts`: normalizes payloads for both agents (`normalize`, `detectAgent`, `phaseOf`) and holds the tool lists and the `apply_patch` parser. Its shell-text parsers are `fileOps`, `writeTargets`, `shellWrites`, `shellEdits` and in-place `sed`/`perl`. It reads exit codes from three places: the PostToolUseFailure `error`, the edges of the output, and the Codex rollout tail|`canny/src/events.ts:49-212, 240-474`|SOLID|
|1.4|`hook.ts`: the decision logic for each phase: `brief` (SessionStart), `pre`, `post`, `stop`. Also `decideStop` (a pure function), `serialize` (agent JSON) and `record` (appends verdicts)|`canny/src/hook.ts:45-58, 60-254, 299-363`|SOLID|
|1.5|`checks.ts`: deterministic classifiers. `isVerify`, `withPipefail`, `projectCheck`, `isIgnored`/`userIgnored`/`isScratch`, `findSecrets`, `isPrivateEnv` (runs `git check-ignore`), `isTestFile`/`testDamage`, `plain`, `fingerprint`, `sha`|`canny/src/checks.ts:8-250`|SOLID|
|1.6|`ledger.ts`: the Fact and Entry types, the session file path, `toFact`, `append`, `read`, `summarize`, the project lookup, the error-log reader and the session listing|`canny/src/ledger.ts:16-228`|SOLID|
|1.7|`jev.ts`: `makeJudge` (an HTTP client with a content-hash cache), the thresholds `YES`/`NO`, and the `noul` question builder|`canny/src/jev.ts:7-124`|SOLID|
|1.8|`rules.ts`: loads project rules. It uses `.canny.json` `rules`, or else extracts bullets from `CLAUDE.md`, `AGENTS.md` and `.claude/CLAUDE.md`|`canny/src/rules.ts:15-70`|SOLID|
|1.9|`config.ts`: the `Config` schema, `home()`, `errorLog()`, `off()`, the trust store, and `.canny.json` discovery|`canny/src/config.ts:7-106`|SOLID|
|1.10|`install.ts`: the hook entries for each agent (`hookConfig`), the settings merge with an atomic write (`merge`), and recognition of Canny's own entries (`isCannyHook`)|`canny/src/install.ts:24-140`|SOLID|
|1.11|Zero runtime dependencies: `src/` imports only `node:` builtins (child_process, crypto, fs, os, path, url, util) and local modules. `package.json` has no `dependencies` key, only `devDependencies`|`grep -hoE 'from "[^".][^"]*"' src/*.ts`; `canny/package.json:50-57`|SOLID|

### 1b. Data flow from a hook event to a verdict

| # | Step | Anchor | Grade |
|---|---|---|---|
|1.12|The agent runs `<cli> hook --agent claude\|codex` (the command `init` wrote) and pipes the payload to stdin|`canny/src/install.ts:39-46`; `canny/src/cli.ts:89`|SOLID|
|1.13|`normalize(raw, agent)` sets the phase from `hook_event_name`: `SessionStart`→start, `PreToolUse`→pre, `PostToolUse`/`PostToolUseFailure`→post, `Stop`→stop, any other name→other. The session is `session_id`, or `"unknown"`. The cwd is the payload `cwd`, or `process.cwd()`. The event is one of edit, command, stop or other|`canny/src/events.ts:64-131, 135-149`|SOLID|
|1.14|The ledger file is `<CANNY_HOME>/sessions/<agent>-<session_id with [^\w.-] replaced by _>.jsonl`|`canny/src/ledger.ts:50-53`|SOLID|
|1.15|The config is `loadConfig(ctx.cwd)`: the nearest `.canny.json`, with its untrusted weakening fields dropped|`canny/src/cli.ts:93`; `canny/src/config.ts:70-77`|SOLID|
|1.16|`handle` dispatches by phase. start→`brief`: a note, nothing recorded. pre→`pre`: the pattern checks; only a non-allow verdict is recorded. post→`post`: appends the fact, then returns a repeat-failure note or runs the Jev rule check. stop→`stop`: appends the stop fact, summarizes, optionally asks Jev whether the message claims done, runs `decideStop`, and always records the verdict. other→allow|`canny/src/hook.ts:45-58, 60-69, 71-139, 161-182, 221-234`|SOLID|
|1.17|`serialize(ctx, decision, raw)` returns the one JSON object written to stdout|`canny/src/hook.ts:303-335`; `canny/src/cli.ts:98`|SOLID|

### 1c. What blocks and what only nags: README against code

| # | README (verbatim or abridged) | Code | Recorded as | Grade |
|---|---|---|---|---|
|1.18|"A code file changed and no test, build, lint, or type-check command has passed since · Stop · ledger · block" (`canny/README.md:131`)|`decideStop` returns `block` (`canny/src/hook.ts:246-253`), serialized as `{decision:"block", reason, systemMessage}` (`:315-316`). A `warn` step comes before it (`:247-251`); README.md:149 describes that step|consistent|SOLID|
|1.19|Secrets "· PreToolUse · pattern · deny" (`canny/README.md:132`)|Edit path `canny/src/hook.ts:76-79`; command path `:90-99`; output `permissionDecision:"deny"` (`:305-313`)|consistent (the pattern wording differs, see 2.24)|SOLID|
|1.20|Test removal "· PreToolUse · pattern · ask on Claude Code, deny on Codex" (`canny/README.md:133`)|`canny/src/hook.ts:81-84, 100-116`; `permissionDecision: d.kind === "ask" && ctx.agent === "claude" ? "ask" : "deny"` (`:311`)|consistent|SOLID|
|1.21|A check piped into `tail` "· PreToolUse · pattern · rewritten to run behind `set -o pipefail`" (`canny/README.md:134`)|`canny/src/hook.ts:117-118, 131-137` → `updatedInput` (`:317-327`). This happens only when `ctx.tool === "Bash"`; PowerShell is not rewritten (`canny/test/hook.test.ts:571`)|consistent|SOLID|
|1.22|"The same command fails with the same output again · **PostToolUse** · ledger · note on the second, deny on the fourth attempt" (`canny/README.md:135`)|The note comes from `post()` at n ≥ 2 (`canny/src/hook.ts:166-173`). **The deny comes from `pre()`, a PreToolUse decision**, when a recorded failure bucket with the same command text has n ≥ 3 (`:119-130`)|MISMATCH in the "When" column|SOLID|
|1.23|"Does this edit break a rule in `CLAUDE.md` or `AGENTS.md`? · PostToolUse · Jev · note" (`canny/README.md:136`)|`ruleCheck` returns `note` or `allow` only (`canny/src/hook.ts:184-219`). A note becomes `hookSpecificOutput.additionalContext` (`:328-329`). The code also reads `.claude/CLAUDE.md` (`canny/src/rules.ts:21`)|consistent|SOLID|
|1.24|"Does this message claim the work is done? · Stop · Jev · can only relax the done-gate" (`canny/README.md:137`)|The only Jev-dependent branch in `decideStop` returns `allow` (`canny/src/hook.ts:252`)|consistent|SOLID|
|1.25|"Only the pattern checks and the ledger gate can block. Everything Jev says becomes a note." (`canny/README.md:123`)|Three decisions stop a tool call or a turn: `deny`, `ask`, `block` (`canny/src/hook.ts:305-316`). No Jev-dependent branch produces any of them (3.15-3.19)|consistent|SOLID|
|1.26|"Codex has no such decision, so it gets a deny with the same reason; **the reason says how to allow it in `.canny.json`** if the removal was intended." (`canny/README.md:139`)|The reason strings are `describe()` + `TESTS_STAY` ("Tests are only removed or skipped when the user asked for it. Fix the code the test covers instead.") and the `rm`/`mv` message (`canny/src/hook.ts:107-110, 271-289`). None of them mentions `.canny.json` or `allow`: `grep 'canny\.json' src/hook.ts` finds nothing|MISMATCH (the claimed reason text is not found)|SOLID|
|1.27|The flowchart (`canny/README.md:109-121`) shows Stop → ledger → Jev → allow or block|It has no node for the `warn` branch (`canny/src/hook.ts:247-251`), which the prose describes at README.md:149|diagram omits a branch|SOLID|
|1.28|Nags, which stop nothing: the SessionStart note (`canny/src/hook.ts:61-69`), the PostToolUse repeat note (`:169-173`), the Jev rule note (`:217-218`), and the Stop `warn`, which serializes to `{systemMessage}` only (`:247-251, 330-331`)|as cited|—|SOLID|
|1.29|Fail-open: any exception in the hook writes an `errors.log` line and stdout gets `{}` (`canny/src/cli.ts:88-98`). The catch block's own `mkdirSync`/`appendFileSync` calls (`:95-96`) are not wrapped. If they throw, `process.stdout.write` (`:98`) is not reached, and the exit status in that case was not determined (NOT run)|`canny/src/cli.ts:85-99`|—|SOLID (text) / UNSURE (runtime)|

## 2. The done-gate

### 2a. The predicate

| # | Fact | Anchor | Grade |
|---|---|---|---|
|2.1|`decideStop(s, stopHookActive, claimsDone, config)` checks four steps in order. (1) `!s.codeFiles.length \|\| s.verified` → allow. (2) `stopHookActive && s.factsSinceBlock === 0 && !config.strict` → warn. (3) `claimsDone !== undefined && claimsDone <= NO` (NO = 0.1) → allow. (4) Otherwise → block, with a reason naming up to 3 files, the last command and its exit code, and what counts as a check|`canny/src/hook.ts:240-264`; `canny/src/jev.ts:13`|SOLID|
|2.2|The inputs. `s = summarize(read(file))`, read AFTER the stop fact is appended. `stopHookActive` = payload `stop_hook_active === true`. `claimsDone` = the Jev `claims_done` answer, requested only when `s.codeFiles.length && !s.verified && message`|`canny/src/hook.ts:223-232`; `canny/src/events.ts:78-84`|SOLID|
|2.3|The Jev call is made before `decideStop` runs, so it is also made when step (2) returns `warn`|`canny/src/hook.ts:226-233`|SOLID|
|2.4|`summarize` walks the entries in order. A `verdict` entry with decision `block` sets `factsSinceBlock = 0`. Stop facts are skipped. Any fact with a non-empty `code` resets `verified = null` and adds new paths to `codeFiles` in first-seen order. A command fact with `verify && exitCode === 0` sets `verified`. Every non-null, non-zero exit increments `repeats[fingerprint]`. After a block, each code-bearing or command fact increments `factsSinceBlock`; it is -1 if nothing was ever blocked|`canny/src/ledger.ts:138-173`|SOLID|
|2.5|README "The done-gate, exactly", steps 1-5 (`canny/README.md:145-151`), maps to 2.1. Step 3's "allow, and warn the user" is the `warn` decision. Its sentence "Claude Code caps consecutive blocks at eight" (`:149`) is a claim about Claude Code: `grep -Ei 'eight\|consecutive\|\b8\b' src/*.ts` finds nothing in Canny|`canny/README.md:145-153`|SOLID (the mapping) / UNSURE (the Claude Code cap is external)|

### 2b. How "a check" is recognized

| # | Fact | Anchor | Grade |
|---|---|---|---|
|2.6|`isVerify(command, config)` first drops quoted strings and `#` comments (`executed`). The pipefail state is taken from the last `set [-+]…o pipefail` statement. Only the LAST statement, split at `;` or a newline, is inspected. It counts if ANY of its `&&` parts: has no `\|\|`; has no `\|` unless pipefail is on; has no lone `&`; has a pre-pipe command that is not `notACheck`; and matches `config.verify` (when set) or else the built-in `VERIFY`. `notACheck` means a first word of echo, printf, cat, grep, rg, ls, which, type, command, man, head, tail or git; `--version` or `--help`; or a leading `!`|`canny/src/checks.ts:31-50, 58-80`|SOLID|
|2.7|The built-in `VERIFY` has 3 regexes. Tests: 33 top-level alternatives (e.g. `pytest`, `vitest`, `jest`, `go test`, `cargo test`, `node --test`, `npm test`, `make test`, `python -m pytest`, `tox`, `nox`). Builds: 20 (e.g. `tsc`, `cargo build`, `go vet`, `mvn (package\|compile\|verify)`, `vite build`, `webpack`). Lint and type-check: 25 (e.g. `eslint`, `oxlint`, `ruff (check\|format --check)`, `mypy`, `pyright`, `golangci-lint`, `cargo clippy`, `pre-commit run`, `shellcheck`). That is 78 in total; the README says "about eighty" (`canny/README.md:198`)|`canny/src/checks.ts:8-12` (the three regexes are lines 9, 10 and 11); counted by an inline Python split of each regex at its top-level `\|`|SOLID|
|2.8|"Passing" means the recorded command fact has `verify === true` and `exitCode === 0`. A null exit code does not count|`canny/src/ledger.ts:168`|SOLID|
|2.9|Where the exit code comes from. Claude PostToolUseFailure: `^Exit code (\d+)` in `error`. Claude PostToolUse: a structured field (`exit_code`/`exitCode`, top-level or under `metadata`), else `exitFromText(output)`, else **0**. Codex: the structured field, else the rollout `item_completed.exit_code`, else `exitFromText(output)`, else null. `exitFromText` searches only the first 3 and the last 3 output lines|`canny/src/events.ts:175-200, 414-426`|SOLID|
|2.10|`withPipefail` returns `set -o pipefail && <cmd>` only when three things hold: the command does not already count, it would count with pipefail, and every pipe in it goes into `tail`|`canny/src/checks.ts:82-93`|SOLID|

### 2c. What counts as "an edit"

| # | Fact | Anchor | Grade |
|---|---|---|---|
|2.11|Edit events: Claude `Write` (the whole file; for the test checks, the `removed` text is read from disk), `Edit`, `MultiEdit`, `NotebookEdit`; Codex `apply_patch` (its Add, Update and Delete File sections)|`canny/src/events.ts:89-122, 151-167`; `canny/src/checks.ts:220-223`|SOLID|
|2.12|Command events also carry `changedFiles`. That is Claude's `tool_response.bashEditDiff.changedFiles` plus files read from the command text: `>`/`>>` targets, `tee` targets, files of in-place `sed -i`/`perl -pi`, `cp`/`mv` destinations, `rm`/`git rm` arguments, `mv` sources, paths after `git checkout --`, and `git restore` paths (not `--staged` alone). Heredoc bodies are not parsed as shell|`canny/src/events.ts:174, 201-210, 240-283, 325-343`|SOLID|
|2.13|Not read, per the code's own comments: `find -exec rm`, `xargs rm`, a second heredoc on one command line, text an interpreter writes (`python -c`, `node -e`), a `sed` delete by line number, and a `-f` script file|`canny/src/events.ts:241, 286, 386`; `canny/README.md:153`|SOLID|
|2.14|A path becomes a "code edit" only after the `toFact` `code` filter. It must not be scratch (under `/tmp`, `/var/tmp` or `/var/folders` and outside cwd). It is made relative to cwd. It must not match `isIgnored`: the `IGNORE` regex plus `config.ignore`. `IGNORE` matches `docs?/` directories, `node_modules`, `.venv`, `__pycache__`, `coverage`, `.cache`, `.git`, and the extensions md, mdx, txt, rst, adoc, svg, png, jp(e)g, gif, ico, webp, lock, log|`canny/src/ledger.ts:66-70`; `canny/src/checks.ts:131-153`|SOLID|
|2.15|README: "Docs, images, and lockfiles do not count as code." (`canny/README.md:147`). Code: `IGNORE` matches only the `.lock` extension, and the test table pins `["pnpm-lock.yaml", false]`, so `pnpm-lock.yaml` is not ignored|`canny/src/checks.ts:131-132`; `canny/test/checks.test.ts:143`|SOLID (contradiction recorded)|

### 2d. "The same command failed with the same output three times"

| # | Fact | Anchor | Grade |
|---|---|---|---|
|2.16|`fingerprint(command, output)` = the first 16 hex characters of sha256(command + "\n" + tail). The tail is the last 30 lines of the last 8,000 characters, with ANSI stripped, durations replaced by `T`, ISO-like timestamps replaced by `TS`, and runs of spaces and tabs collapsed|`canny/src/checks.ts:232-250`|SOLID|
|2.17|Every command fact with a non-null, non-zero exit increments `repeats[fingerprint].n`|`canny/src/ledger.ts:164-167`|SOLID|
|2.18|A PostToolUse note fires when that fingerprint's n ≥ 2 (`REPEAT_NOTE_AT`). A PreToolUse deny fires when any bucket has `command === plain(rewritten ?? command)` and n ≥ 3 (`REPEAT_DENY_AFTER`). The code comment: "the agent is told at the second one and stopped after the third"|`canny/src/hook.ts:32-34, 119-130, 166-173`|SOLID|
|2.19|`repeats` is never reset within a session: `summarize` has no reset, and the deny lookup has no condition on edits made since the failures. The deny text reads "Change the code or the approach first." A different command text, such as one with extra flags, is allowed (`canny/test/hook.test.ts:420-422`)|`canny/src/ledger.ts:138-173`; `canny/src/hook.ts:119-130`|SOLID (text; NOT run)|
|2.20|`allow: ["repeat-failure"]` turns off both the note and the deny|`canny/src/hook.ts:119, 167`|SOLID|

### 2e. The secret-detection rule

| # | Fact | Anchor | Grade |
|---|---|---|---|
|2.21|`SECRETS`, each a label and a regex. AWS access key `\bAKIA[0-9A-Z]{16}\b`. GitHub token `\b(gh[pousr]_[A-Za-z0-9]{36,}\|github_pat_[A-Za-z0-9_]{22,})\b`. Slack token `\bxox[baprs]-[A-Za-z0-9-]{10,}`. Private key `-----BEGIN (?:RSA \|EC \|DSA \|OPENSSH \|PGP )?PRIVATE KEY(?: BLOCK)?-----`. OpenAI or Anthropic key `\bsk-(?:ant-\|proj-)?[A-Za-z0-9_-]{24,}\b`. Stripe key `\b[sr]k_(?:live\|test)_[A-Za-z0-9]{20,}\b`. Google API key `\bAIza[0-9A-Za-z_-]{35}\b`. Hardcoded credential, case-insensitive: `(?:api[_-]?key\|secret\|token\|passw(?:or)?d)\s*[:=]\s*`, then an opening quote (double, single or backtick), then ≥ 16 non-space, non-quote characters that contain a digit and a letter, then a closing quote|`canny/src/checks.ts:155-167`|SOLID|
|2.22|The scanned text. For edits, only the `added` text: Write content, Edit `new_string`, MultiEdit new strings, NotebookEdit `new_source`, apply_patch `+` lines. For commands, heredoc bodies and any `echo`/`printf` statement that redirects or `tee`s into a file (`shellWrites`)|`canny/src/hook.ts:76-79, 90-99`; `canny/src/events.ts:306-323`|SOLID|
|2.23|The exemption, `isPrivateEnv`. The path must match `(^\|/)\.env(\.[^/]*)?$`; must not end in `.example`, `.sample`, `.template` or `.dist`; must not be a symlink; and `git check-ignore -q <path>` must exit 0 (2 s timeout). For shell writes there is one more condition: any `cd`/`pushd`/`popd` cancels the exemption, except a single opening `cd` to `.`, `./`, `"$PWD"` or the cwd's own absolute path|`canny/src/checks.ts:169-183`; `canny/src/hook.ts:92-95, 141-159`|SOLID|
|2.24|README wording: "AWS, GitHub, Slack, Stripe, Google, OpenAI or Anthropic keys, private key blocks, or `password = "…"` with real-looking entropy" (`canny/README.md:132`). The code's generic rule keys on the names `api_key`/`apikey`/`api-key`, `secret`, `token` and `password`/`passwd`, not only `password`|`canny/src/checks.ts:163-166`|SOLID (wording difference recorded)|

## 3. The Jev client (`src/jev.ts`)

### 3a. The client

| # | Fact | Anchor | Grade |
|---|---|---|---|
|3.1|Endpoint `JEV_URL = process.env.CANNY_JEV_URL ?? "https://api.typesafe.ai/v1/systemone"`. Model `CANNY_JEV_MODEL ?? "jev-latest"`. Timeout `Number(CANNY_JEV_TIMEOUT_MS ?? 3000)` ms. All three are read once, at module load. There is no config-file key for any of them: the `Config` interface has no URL, model or timeout field|`canny/src/jev.ts:7-9`; `canny/src/config.ts:7-19`|SOLID|
|3.2|The request: `POST JEV_URL` with headers `Authorization: Bearer <TYPESAFE_API_KEY>`, `Content-Type: application/json` and `Accept: application/json`. The body is `JSON.stringify({ state, model, questions })`. The call uses `signal: AbortSignal.timeout(TIMEOUT_MS)`|`canny/src/jev.ts:75, 92-101`|SOLID|
|3.3|Question type: `noul` only, shaped `{type:"noul", instructions, criteria?:{true, false}}`|`canny/src/jev.ts:15-19, 33-37`|SOLID|
|3.4|Two question families. `claims_done` has the instructions "Does `message` claim that the requested work is complete?" plus true and false criteria. Its state is `{message}`: the whole last assistant message, not clipped. `rule_<i>` is asked once per rule, with the instructions "Does the code change in `change` break the project rule in `rules[<i>]`?". Its state is `{rules, change:{file, added, removed}}`, where `added` and `removed` are clipped to 4,000 characters plus `"\n[clipped]"`|`canny/src/hook.ts:37-43, 194-209, 227-230, 367`|SOLID|
|3.5|Request count. The rule check sends one request per changed file, with every rule (at most 24) as a question in that request; files go in parallel (`Promise.all`). A Stop sends one request with one question|`canny/src/hook.ts:194-216`; `canny/src/rules.ts:8, 17-18, 29`|SOLID|
|3.6|Parsing the response. `res.ok` is required; otherwise the client throws `Error("HTTP <status>")`. It reads `json.answers?.[id]?.noul` and keeps only values where `typeof === "number"`. Missing ids are dropped without notice. There is no range check: any JSON number is accepted. `model` and `usage` are not read|`canny/src/jev.ts:102-108`|SOLID|
|3.7|Retries: none. There is one `doFetch` per call; the only retry loop in `src/` is the Codex rollout read|`canny/src/jev.ts:92`; `canny/src/events.ts:438-445`; `grep -Ei 'retr(y\|ies)\|attempt\|backoff' src/*.ts`|SOLID|
|3.8|The cache. Key = sha256(JSON.stringify({state, model, questions})); the URL is NOT part of the key. File = `<CANNY_HOME>/jev/<hash>.json`, holding `{body, answers, ts}`. It is written only on HTTP success, as a temp file (`<file>.<uuid>.tmp`, flag `wx`, mode 0600) renamed into place, in a 0700 directory; a write failure is swallowed. `ts` is never read, so entries do not expire. Cached `answers` are returned without validation. A damaged file reads as a miss|`canny/src/jev.ts:39-41, 48-69, 76-87, 109`|SOLID|
|3.9|Order: the cache lookup (`:79-87`) runs BEFORE the key check (`:88-89`). A cache hit returns answers when no key is set, and the test asserts this: it deletes the key, then gets the cached answer back|`canny/src/jev.ts:79-89`; `canny/test/jev.test.ts:35-38`|SOLID|
|3.10|Fail-open. No key and no cache → `null`, and NOTHING is logged. An HTTP, timeout or parse error is logged as `{hash, ids, cached:false, ms, answers:null, error}` and the call returns `null`. The consumers treat `null` as "no answer"|`canny/src/jev.ts:88-89, 112-122`|SOLID|
|3.11|Logging: every logged call is appended to the session ledger as `{ts, type:"jev", hash, ids, cached, ms, answers[, error]}`. The request body is not in the ledger; it is in the cache file|`canny/src/cli.ts:92`; `canny/src/jev.ts:24-31, 82, 110, 113-120`|SOLID|
|3.12|The base URL is configurable through the env var `CANNY_JEV_URL` only (`canny/README.md:165, 170`). The code restricts neither scheme nor host|`canny/src/jev.ts:8, 92`|SOLID|
|3.13|The tests mock `fetchFn`; no test contacts a live endpoint. The README says: "covered by tests with a mocked endpoint"|`canny/test/jev.test.ts:6-18`; `canny/README.md:247`|SOLID|

### 3b. The request contract beside our System One endpoint (facts on both sides; the pair was NOT run together)

| # | Aspect | canny (client) | af `scripts/laya_systemone_server.py` (server) | Grade |
|---|---|---|---|---|
|3.14|Path and method|POST to the full `CANNY_JEV_URL` (`canny/src/jev.ts:8, 92-93`)|POST `/v1/systemone` only; any other path gets 404 (`af/scripts/laya_systemone_server.py:170-172`). It binds loopback only, default `127.0.0.1:47411` (`:205-206, 213-215`)|SOLID|
|3.15|Auth|`Authorization: Bearer <TYPESAFE_API_KEY>`. NO request is sent when the env var is unset or empty (`canny/src/jev.ts:88-89, 95`)|"The bearer token is not checked (the endpoint is loopback-only; there is no second tenant); a client's `authorization` header is ignored." (`af/scripts/laya_systemone_server.py:15-16`)|SOLID|
|3.16|Body|`{state, model, questions}` (`canny/src/jev.ts:75`)|`{"model": <ignored>, "state": <str\|dict\|list>, "questions": {id: {...}}}` (`:5`). It returns 400 unless `state` is present and `questions` is a non-empty object. The body must be 1 byte to 8 MiB (`:29, 173-181`)|SOLID|
|3.17|Question|`type:"noul"`, `instructions`, optional `criteria` (`canny/src/jev.ts:15-19`)|`type` must be `noul`, `choice` or `score` (`:182-184`); other keys pass through to `system_one` (`:134`)|SOLID|
|3.18|State shape|`{message}`, or `{rules:[…], change:{file, added, removed}}` (`canny/src/hook.ts:206-209, 228`). There is no `chunks` key|Fan-out, one call per chunk, happens ONLY when `state.chunks` is a list of `{id, text}` and every question id names a chunk. Otherwise there is ONE `system_one(state, questions)` call (`:118-134`)|SOLID|
|3.19|Response|reads `answers[id].noul` numbers (`canny/src/jev.ts:103-108`)|200 `{"model", "answers": {id: {"type", "noul": <float>, ...}}, "usage"}` (`:6`), plus `latency_ms` (`:199-200`) and `fan_out` on the chunk path (`:144`). 502 when the answer ids differ from the question ids (`:196-198`); 503 when the model is not loaded (`:185-186`); 500 on a model error (`:194-195`)|SOLID|
|3.20|Timeout and latency|3,000 ms per request by default (`canny/src/jev.ts:9, 100`)|Our measurement: "About 1.0-1.25 s per (state, question) pair on CPU float32, on BOTH venues"; "Batching did NOT amortize" (`af/docs/research/findings/JEV-LAYA-AUDIT-2026-09-22.md:133-136`). The PC live smoke of a 3-chunk request took 25,298.6 ms on the first run and 944.4 ms on the second (`af/tasks/briefs/jev-laya/PCJ1-report.md:20-21`. The file is untracked and was edited during this lane: mtime 2026-09-23 00:17:04Z, and the lines moved from 18-19 to 20-21)|SOLID (both sides cited)|
|3.21|Several questions against one state|Canny's rule check sends up to 24 `rule_<i>` questions against one state (3.5)|The server docstring records this for the batch form: "the open model answers ONE value for the whole batch (0.598 for three unlike chunks)" (`:9-11`). What it answers for Canny's multi-rule shape, which is not a chunk batch, was NOT measured|UNSURE|
|3.22|Cache and endpoint|The cache key excludes the URL (`canny/src/jev.ts:75-78`), so an answer cached from one endpoint is returned for another|—|SOLID|

### 3c. Every place a Jev probability is consumed

| # | Site | What happens | Can it block? | Grade |
|---|---|---|---|---|
|3.23|`canny/src/hook.ts:210-211` (`ruleCheck`)|`(answers?.[rule_i] ?? 0) >= YES` (0.9) → the rule is listed in a `note` (`:212-218`). The only decision kinds here are `note` and `allow`|NO|SOLID|
|3.24|`canny/src/hook.ts:227-231` (`stop`) → `:252`|`claimsDone = answers?.[claims_done]`. In `decideStop`, `claimsDone !== undefined && claimsDone <= NO` → `allow`. The `block` at `:253` is reached when `claimsDone` is undefined or > 0.1|NO: it can only turn a block into an allow|SOLID|
|3.25|`canny/src/cli.ts:256-262` (`replay`)|Reads the recorded `answers.claims_done` of the first `jev` entry between a stop event and the next verdict, and passes it to `decideStop`. The output is a printed comparison, plus exit 1 on any mismatch|NO (produces no hook decision)|SOLID|
|3.26|`canny/src/cli.ts:222, 240-242` (`status`)|Counts `jev` entries, how many were cached and how many failed. It reads no probability|NO|SOLID|
|3.27|Completeness: `grep -nE '\bjudge\b\|\banswers\b\|\bYES\b\|\bNO\b\|claimsDone\|CLAIMS_DONE_ID'` over `src/*.ts` finds only jev.ts, the hook.ts lines above, and `cli.ts:16, 92-93, 222, 258, 262`|—|—|SOLID|
|3.28|Out-of-range values: nothing is clamped. A value ≤ 0.1, including a negative one, relaxes the Stop gate; a value ≥ 0.9, including one above 1, notes a rule|`canny/src/jev.ts:106-107`; `canny/src/hook.ts:211, 252`|NO|SOLID (text)|

### 3d. README against code for Jev

| # | README | Code | Grade |
|---|---|---|---|
|3.29|"If you would rather not, leave the key unset: the ledger, the done-gate, and the pattern checks work exactly the same, and only the two judgment questions go unanswered." (`canny/README.md:165`)|Cached answers are returned without a key (3.9), and a test pins it|SOLID (contradiction recorded)|
|3.30|"**Log everything.** Each call, its hash, its latency, and its answers go into the session ledger" (`canny/README.md:163`)|The no-key, no-cache path returns before any log call (`canny/src/jev.ts:88-89`)|SOLID (contradiction recorded)|
|3.31|"A rule is reported broken above 0.9. A message is treated as "not a done claim" below 0.1." (`canny/README.md:162`)|The code compares inclusively: `>= YES` (`canny/src/hook.ts:211`) and `<= NO` (`:252`). README.md:150 says "at least 90 percent sure", which is also inclusive|SOLID (boundary wording recorded)|
|3.32|"Without a key, nothing leaves the machine." (`canny/README.md:179`)|No fetch happens without a key (`canny/src/jev.ts:88-89`)|SOLID (consistent)|

## 4. The ledger

### 4a. Format, location, write discipline, identity

| # | Fact | Anchor | Grade |
|---|---|---|---|
|4.1|Location: `<CANNY_HOME or ~/.canny>/sessions/<agent>-<session_id with [^\w.-] replaced by _>.jsonl`. A payload with no `session_id` gets `unknown`, so all such payloads share one file per agent|`canny/src/ledger.ts:50-53`; `canny/src/config.ts:22`; `canny/src/events.ts:73`; `canny/test/ledger.test.ts:6-16`|SOLID|
|4.2|Format: JSON Lines with three entry types. `event` = {ts, type, cwd, phase, hookEvent, tool, fact}. `verdict` = {ts, type, cwd, phase, decision, message?}. `jev` = {ts, type, hash, ids, cached, ms, answers, error?}. `ts` = `Date.now()` in ms|`canny/src/ledger.ts:37-48`; `canny/src/hook.ts:343-363`; `canny/src/cli.ts:92`|SOLID|
|4.3|Facts. `edit` = {files, deleted, code}. `command` = {command, exitCode, verify, fingerprint, summary, code}, where `summary` is the last non-empty output line, at most 200 characters. `stop` = {stopHookActive, messageHash}, where `messageHash` is 16 hex characters of sha256. Every string passes through `plain`, which strips ANSI and control characters|`canny/src/ledger.ts:16-30, 61-98`; `canny/src/checks.ts:197-201`|SOLID|
|4.4|What each event writes. PostToolUse and PostToolUseFailure: an `event` when a fact results, plus a `note` verdict if one is made. PreToolUse: a `verdict` only for deny, ask or rewrite. Stop: the `event`, then a `jev` entry if one is logged, then a `verdict`, always (allow included). SessionStart: nothing ("Nothing is recorded")|`canny/src/hook.ts:60, 71, 164-165, 223, 233, 353-363`; `canny/test/hook.test.ts:592`|SOLID|
|4.5|Write discipline. `append` runs `mkdirSync(dir, {mode:0o700})`, then one `appendFileSync(file, JSON + "\n", {mode:0o600})` per entry. The code comment: "Append-only so parallel hook processes never clobber each other". There is no lock, no fsync, and no temp file + rename. The mode applies at file creation only (`canny/CHANGELOG.md:74`)|`canny/src/ledger.ts:100-104`; `grep -Ei 'flock\|lockfile' src/*.ts` → none|SOLID (text) / UNSURE (whether concurrent appends from several processes stay whole lines; the code does not assert it)|
|4.6|Read discipline: a missing or unreadable file reads as `[]`, and lines that do not parse are skipped (the half-written-line test)|`canny/src/ledger.ts:106-124`; `canny/test/ledger.test.ts:18-34`|SOLID|
|4.7|Identity and digests. Entries have no id, no sequence number, no hash chain and no MAC or signature: `grep -Ei 'hmac\|signature\|chain' src/*.ts` finds nothing. The digests present are `fingerprint` (16 hex), `messageHash` (16 hex) and the jev `hash` (64 hex)|`canny/src/checks.ts:236-250`; `canny/src/ledger.ts:93`; `canny/src/jev.ts:39`|SOLID|
|4.8|Project identity. Every `event` and `verdict` carries `cwd`. `sessionCwd` = the cwd of the first non-jev entry. `latestSession(cwd)` reads the ledgers newest-mtime first until one belongs to the same project, meaning either directory contains the other, with symlinks resolved|`canny/src/ledger.ts:175-203`; `canny/src/hook.ts:346, 356`|SOLID|
|4.9|README: "Every hook event lands in an append-only ledger … Only paths and outcomes are stored, never file contents." (`canny/README.md:89`). Code: SessionStart events and allowed PreToolUse events are not written (4.4). The `command` field stores the full command text via `plain(event.command)` (`canny/src/ledger.ts:81`); for a heredoc write, that text includes the body. README.md:177 says separately: "keeps the command line of every shell command … A secret passed on a command line does end up in the ledger."|both cited|SOLID (contradiction recorded, both sides)|

### 4b. `canny replay`: what is replayed and what is compared

| # | Fact | Anchor | Grade |
|---|---|---|---|
|4.10|`canny replay [file]` uses the given file, or else the latest session of the current directory's project|`canny/src/cli.ts:190-199, 246-249`|SOLID|
|4.11|Replayed: for each `event` entry whose fact kind is `stop`, `decideStop(summarize(entries[0..i]), fact.stopHookActive, jev?.answers?.claims_done, config)`. Here `jev` is the first `type:"jev"` entry after the stop event and before the next `verdict` entry|`canny/src/cli.ts:253-264`|SOLID|
|4.12|Compared: only `decision.kind`, against the `decision` of the first `verdict` entry after the stop event, from any phase. Messages are not compared. It prints `#<i> stop recorded=… replayed=… ok\|MISMATCH` and exits 1 on any mismatch|`canny/src/cli.ts:256, 265-273`|SOLID|
|4.13|Not replayed: PreToolUse deny, ask and rewrite verdicts; PostToolUse notes; SessionStart notes. Fact derivation is not re-derived either (the `verify`, `code` and `fingerprint` classifications): the stored facts are used as they are, because raw payloads are not stored|`canny/src/cli.ts:253-255`; `canny/src/ledger.ts:61-98`|SOLID|
|4.14|One input does not come from the ledger: `config` = `loadConfig(sessionCwd ?? process.cwd())` at replay time, which means the current `.canny.json` and trust store. The ledger records no config; `strict` changes the `decideStop` outcome (`canny/src/hook.ts:247`)|`canny/src/cli.ts:250-251`; `canny/src/hook.ts:343-351`|SOLID|
|4.15|The live slice and the replay slice differ. Live, `stop()` summarizes the whole file as read after its own append (`canny/src/hook.ts:223-224`). Replay summarizes the entries up to and including the stop event (`canny/src/cli.ts:260`)|both cited|SOLID (the difference is recorded; its effect was not measured)|
|4.16|Tested: a whole session run through the hook process replays as 3 × `ok`, and an edited verdict (`block`→`allow`) yields `MISMATCH` and exit 1|`canny/test/cli.test.ts:98-138`|SOLID (NOT run here)|
|4.17|README claims: "The same session always produces the same verdict, and `canny replay` proves it from the ledger." (`canny/README.md:35`); "There are none." (`:105`); "Those ledgers replay clean." (`:241`). No ledger file is committed: `git ls-files` lists only three `.jsonl` files, and they are the hook-payload fixtures under `test/fixtures/`|as cited|UNSURE (the claims have no committed artifact)|

## 5. Hook protocol

### 5a. Canny with Claude Code and Codex

| # | Fact | Anchor | Grade |
|---|---|---|---|
|5.1|Claude Code events that `init` registers: SessionStart (timeout 10); PreToolUse (matcher `Write\|Edit\|MultiEdit\|NotebookEdit\|Bash\|PowerShell`, 10); PostToolUse (same matcher, 15); PostToolUseFailure (`Bash\|PowerShell`, 15); Stop (15). Each entry is `{type:"command", command:"<cli> hook --agent claude", timeout, statusMessage:"Canny"}`|`canny/src/install.ts:36-63`; `canny/src/events.ts:54-61`|SOLID|
|5.2|Codex events: SessionStart (10), PreToolUse (`Bash\|apply_patch`, 10), PostToolUse (15), Stop (15). There is no PostToolUseFailure|`canny/src/install.ts:49-55`|SOLID|
|5.3|The JSON read from stdin, whole. Fields: `hook_event_name`, `session_id`, `cwd`, `tool_name`, `tool_input` (an object, or a bare string taken as the command), `tool_response` (an object or a string; reads `stdout`/`stderr`/`output`, `exit_code`/`exitCode`, `metadata.*`, `bashEditDiff.changedFiles`), `error`, `last_assistant_message`, `stop_hook_active`, `transcript_path`, `tool_use_id`. Agent auto-detection: a string `turn_id` or `model` → codex|`canny/src/events.ts:49-52, 64-131, 169-212`|SOLID|
|5.4|The JSON written: one object, by decision. deny/ask → `{systemMessage, hookSpecificOutput:{hookEventName:"PreToolUse", permissionDecision, permissionDecisionReason}}`. block → `{decision:"block", reason, systemMessage}`. rewrite → `{hookSpecificOutput:{hookEventName:"PreToolUse", [permissionDecision:"allow" on Codex only], updatedInput:{…tool_input, command}, additionalContext}}`. note → `{hookSpecificOutput:{hookEventName:<the event>, additionalContext}}`. warn → `{systemMessage}`. allow → `{}`|`canny/src/hook.ts:303-335`; `canny/src/cli.ts:98`|SOLID|
|5.5|Exit codes: the hook path sets no exit code, so blocks travel in JSON, not as exit 2. `process.exitCode` is set only when `init`/`remove` fail and by `replay`|`canny/src/cli.ts:85-99, 141, 273`|SOLID|
|5.6|Whether the agents honor these output shapes at their current versions was not verified here (NOT run). The README claims both were verified live (`canny/README.md:241`). The recorded INPUT fixtures come from Claude Code 2.1.277 and codex-cli 0.154.0 (`canny/CONTRIBUTING.md:50`)|as cited|UNSURE|
|5.7|The recorded Claude fixture's Bash PostToolUse `tool_response` has the keys interrupted, isImage, noOutputExpected, stderr, stdout: no exit code and no `bashEditDiff`. `bashEditDiff` appears only in hand-written tests. Neither fixture contains a SessionStart payload; the recording config lists PreToolUse, PostToolUse, PostToolUseFailure and Stop|`canny/test/fixtures/claude-code.jsonl:8`; `canny/test/hook.test.ts:145`; `canny/test/events.test.ts:81`; `canny/CONTRIBUTING.md:52`|SOLID|
|5.8|The Codex path. `init` writes `.codex/hooks.json`. The exit code comes from the rollout file named by `transcript_path`: the last 512 KiB is scanned backwards for a line containing both the `tool_use_id` and `item_completed`, and `payload.item.exit_code` is read. There are up to 5 retries 10 ms apart (`Atomics.wait`). `apply_patch` text is read from `tool_input.command\|patch\|input`. `ask` becomes `deny`, and a rewrite carries `permissionDecision:"allow"`. `init` prints "Codex asks you to trust new hooks once: run /hooks inside Codex."|`canny/src/cli.ts:121-133`; `canny/src/events.ts:117-122, 196-200, 428-474`; `canny/src/hook.ts:311, 323`|SOLID|

### 5b. The README's "four places they differ" (`canny/README.md:232-241`)

| # | README | Code | Grade |
|---|---|---|---|
|5.9|(1) "Claude Code fires `PostToolUse` only for commands that succeed and `PostToolUseFailure` for the rest … Codex fires `PostToolUse` for both and puts no exit code in the payload at all … If that lookup fails, the exit code is unknown and the command does not count as a passing check." (`:236`)|For Codex the order is: the structured field, then the transcript, then `exitFromText(output)`, then null (`canny/src/events.ts:196-200`). A test reads `"Process exited with code 3\nboom"` as exit 3 for Codex (`canny/test/events.test.ts:121-123`)|SOLID (the README omits the text fallback; recorded)|
|5.10|(2) "Codex has no `ask` decision, so the test-removal check denies there." (`:237`)|`canny/src/hook.ts:311`|SOLID|
|5.11|(3) "Codex file edits arrive as an `apply_patch` document; Canny parses it for files, removed tests, and secrets." (`:238`)|`canny/src/events.ts:117-122, 151-167`; `canny/src/hook.ts:74-86`|SOLID|
|5.12|(4) "Codex asks you to trust hooks once, through `/hooks`. Claude Code picks up hook config from its settings files as you save them." (`:239`)|In code, only the printed hint (`canny/src/cli.ts:123`). The agents' behavior cannot be checked from this repo|UNSURE|

### 5c. `src/install.ts`: which files it writes, and where

| # | Fact | Anchor | Grade |
|---|---|---|---|
|5.13|`init` writes `<root>/.claude/settings.json` and/or `<root>/.codex/hooks.json`. `root` = `process.cwd()`, or `homedir()` with `--global`. With neither `--claude` nor `--codex`, it writes for each of `~/.claude` and `~/.codex` that exists, or for both when neither exists|`canny/src/cli.ts:101-133`|SOLID|
|5.14|The hook command is `canny hook --agent X` when an executable `canny` is on PATH; otherwise `node "<absolute path of dist/cli.js>" hook --agent X`|`canny/src/cli.ts:114-118, 145-164`|SOLID|
|5.15|`merge` parses the existing file. It refuses non-JSON, a non-object, a non-object `hooks` and a non-array event value. It removes every earlier Canny entry, recognized by `statusMessage:"Canny"` + `hook --agent`, or by a leading `canny hook --agent`. It appends Canny's groups AFTER the existing groups of each event. It writes to the realpath target through `<target>.canny-<pid>.tmp` (flag `wx`, keeping the existing mode) and renames it into place. The parent directory is created with no explicit mode|`canny/src/install.ts:20-33, 70-140`|SOLID|
|5.16|`remove` runs `merge(file, {})` on both files, if they exist|`canny/src/cli.ts:166-172`|SOLID|

### 5d. Our side: the Hermes hook events our harness already adapts (facts only; no fit assessed)

| # | Fact | Anchor | Grade |
|---|---|---|---|
|5.17|The hook shim resolves the repo root, exports `CLAUDE_PROJECT_DIR` and execs `.claude/hooks/<name>`, passing stdin, stdout, stderr and the exit code straight through. A missing hook → a stderr line and exit 0|`af/harness-ports/bin/hook-shim.sh:1-46`|SOLID|
|5.18|The adapter docstring. Hermes input is "Claude-Code-compatible on the INPUT side (JSON on stdin: hook_event_name, tool_name, tool_input, session_id, cwd, extra)". The return contract is per event. `pre_llm_call` injects "ONLY via {"context": "..."}". `pre_verify` takes `{"decision":"block","reason":...}` or `{"action":"continue","message":...}`, which "become a CONTINUE NUDGE bounded by agent.max_verify_nudges (3), never a hard block; fires only after code edits". `pre_tool_call` allows "block / modify / approve only — there is NO advisory channel". `post_tool_call`: "Observer. RETURN IS IGNORED". `on_session_start`: an observer|`af/harness-ports/bin/hermes-hook-adapter.py:4-21`|SOLID (a quote of our own doc; the Hermes source was not re-read here)|
|5.19|The event sets. `OBSERVER_EVENTS` = post_tool_call, post_llm_call, on_session_start, on_session_end, subagent_start, subagent_stop, pre_api_request, post_api_request. `INJECT_EVENTS` = pre_llm_call. `BLOCK_EVENTS` = pre_verify, pre_tool_call|`af/harness-ports/bin/hermes-hook-adapter.py:46-51`|SOLID|
|5.20|The translations. `extra.user_message` → `prompt`. The Hermes tool `search_files` → `Grep`. `patch`/`write_file` → `Edit`, with `file_path` and `new_string` filled from `path`/`file` and `content`/`new_str`. For block events, exit 2 + stderr → `{"decision":"block","reason":<stderr>}`; otherwise non-empty stdout → a block with stdout as the reason. Observer output is dropped with a stderr note, or with `--spool` appended to a per-session spool that the next `pre_llm_call` drains|`af/harness-ports/bin/hermes-hook-adapter.py:118-133, 146-205`|SOLID|
|5.21|What the config snippet wires. `on_session_start` → hook-shim session-start.sh (`:129-131`). `pre_llm_call` → the adapter with wiki-context.py and `--spool` (`:137-139`). `post_tool_call` with matcher `patch\|write_file` → edit-snapshot.py `--spool` (`:154-157`). `post_tool_call` with matcher `search_files` → graft-first-nag.py `--spool` (`:162-164`). `pre_verify` → turn-retro-gate.sh is COMMENTED OUT ("OFF FOR BUILD LANES", `:166-178`). `pre_tool_call` → graft-first-nag is COMMENTED OUT ("NOT WIRED — deliberately", `:180-194`)|`af/harness-ports/hermes/config-snippet.yaml:124-194`|SOLID|
|5.22|The adapter test has 6 cases: pre_verify positive (the retro gate's exit 2 becomes a block); pre_tool_call positive (search_files is mapped to Grep and the nag fires); pre_tool_call negative (a literal-token sweep stays silent); pre_llm_call positive (a context envelope); post_tool_call observer (stdout empty, "OBSERVER" on stderr); on_session_start observer|`af/harness-ports/tests/test_hermes_hook_adapter.py:129-161`|SOLID (NOT run here)|
|5.23|The name of the Hermes shell tool in our docs: "behind a `terminal` command wrapper, wired by the `pre_tool_call` MODIFY seam"|`af/docs/research/findings/JEV-LAYA-AUDIT-2026-09-22.md:181-183`|SOLID (as a quote)|
|5.24|Canny's side, for the same comparison (no assessment). Event names it recognizes: SessionStart, PreToolUse, PostToolUse, PostToolUseFailure, Stop; any other name → `other` → allow. Tool names it recognizes: Write, Edit, MultiEdit, NotebookEdit, Bash, PowerShell, apply_patch. Stop fields it reads: `last_assistant_message`, `stop_hook_active`|`canny/src/events.ts:58-61, 78-84, 89-129, 135-149`|SOLID|
|5.25|The Codex adapter also exists. apply_patch PostToolUse → one synthetic Edit per file; Bash PreToolUse `rg`/`grep` → a Grep-shaped payload; "Verified against openai/codex @ bc39b0ed"|`af/harness-ports/bin/codex-hook-adapter.py:1-40`|SOLID|

## 6. Configuration (`src/config.ts`, `src/rules.ts`)

| # | Fact | Anchor | Grade |
|---|---|---|---|
|6.1|The file is `.canny.json`, the nearest one at or above the payload `cwd`; the search stops at `homedir()`|`canny/src/config.ts:45-63`|SOLID|
|6.2|The schema. `verify?: string[]`: regexes that REPLACE the built-in check list. `ignore?: string[]`: regexes ADDED to `IGNORE`; those paths are also never sent to Jev. `rules?: string[]`: replaces the extraction. `allow?: string[]`: checks to turn off, from `secrets`, `test-removal`, `repeat-failure`, `rules`. `strict?: boolean`|`canny/src/config.ts:7-19`; `canny/README.md:188-202`|SOLID|
|6.3|Trust. `verify`, `ignore`, `rules` and `allow` (the `WEAKENING` list) are deleted unless `trusted.json[<absolute file path>] === sha256(file text)`. `strict` is read even when the file is untrusted. `canny trust` records the current hash without a prompt|`canny/src/config.ts:30-35, 56, 70-88`; `canny/src/cli.ts:174-188`|SOLID|
|6.4|Validation. The code checks only that the value is a JSON object (`canny/src/config.ts:90-98`); field types are not checked. `off()` tests with `.includes(check)` (`:28`), a method that both arrays and strings have. An invalid regex in `verify` or `ignore` compiles to null and never matches (`canny/src/checks.ts:16-27`)|as cited|SOLID (text)|
|6.5|README: "which lands in your shell history and in Canny's own ledger" (`canny/README.md:214`). Code: `canny trust` writes only `trusted.json` (`canny/src/config.ts:80-84`; `canny/src/cli.ts:175-188`). A Bash call to it made through a hooked agent is recorded as a command fact, like any other command (`canny/src/hook.ts:164-165`)|both cited|SOLID (both sides recorded)|
|6.6|Rule format: plain strings. From a trusted `.canny.json`: the first 24. Otherwise the code reads `<cwd>/CLAUDE.md`, `<cwd>/AGENTS.md` and `<cwd>/.claude/CLAUDE.md`, in cwd only with no walk to parent directories. It takes bullet (`-`, `*`, `+`) or numbered (`1.` / `1)`) lines outside code fences, and joins continuation lines that start with 2 or more spaces. A line is kept when it has ≥ 12 characters and matches STRONG `\b(never\|always\|must\|do not\|don't\|no\s+\w)\b` or SOFT `\b(should\|prefer\|avoid\|only\|use\|keep\|run)\b`, case-insensitive. Backticks, bold and links are stripped. Rules are de-duplicated, STRONG rules come first, and the cap is 24. `source` = the names of the files found|`canny/src/rules.ts:6-8, 15-70`|SOLID|
|6.7|"Never hardcode model IDs" is the README's example rule (`canny/README.md:31, 192`). It is tested only with a stub judge that returns 0.95|`canny/test/hook.test.ts:427-452, 478-520`|SOLID|
|6.8|Defaults with no config: the built-in `VERIFY` and `IGNORE`, rules extracted from the agent files, no check turned off, `strict` falsy. Constants: YES 0.9 / NO 0.1; repeat note at 2, deny after 3; clip 4,000; hook timeouts 10/15 s. Env defaults: `CANNY_JEV_MODEL` `jev-latest`, `CANNY_JEV_URL` TypeSafe's URL, `CANNY_JEV_TIMEOUT_MS` 3000, `CANNY_HOME` `~/.canny`|`canny/src/jev.ts:7-13`; `canny/src/hook.ts:33-34, 367`; `canny/src/install.ts:51-61`; `canny/src/config.ts:22`|SOLID|
|6.9|README: `CANNY_HOME` holds "Sessions, cache, error log, and the source checkout" (`canny/README.md:173`). The code uses `home()` for sessions (`canny/src/ledger.ts:50`), the Jev cache (`canny/src/jev.ts:41`), `errors.log` (`canny/src/config.ts:25`) and `trusted.json` (`:86`). No code path reads a checkout under it; the install prompt clones to the literal path `~/.canny/src` (`canny/README.md:57`)|both cited|SOLID (both sides recorded)|

## 7. Egress and side effects (`src/`, plus install time)

| # | Kind | Site and detail | Anchor | Grade |
|---|---|---|---|---|
|7.1|Network|The only network call in `src/`: `fetch` POST to `JEV_URL`. It runs only when `TYPESAFE_API_KEY` is non-empty and the cache misses. It sends the state (the final message, or the rules plus the clipped change), the model and the questions|`canny/src/jev.ts:88-101`; grep for `fetch\|https?://\|node:https?\|node:net\|socket` over `src/*.ts`|SOLID|
|7.2|File write|The ledger: `<home>/sessions/*.jsonl` (0600, directory 0700)|`canny/src/ledger.ts:101-104`|SOLID|
|7.3|File write|The Jev cache: `<home>/jev/<hash>.json`, written via temp file + rename (0600/0700). It holds the request body: clipped diffs, rules, the final message|`canny/src/jev.ts:53-69, 109`|SOLID|
|7.4|File write|`<home>/errors.log` (0600/0700), written on a hook crash|`canny/src/cli.ts:95-96`|SOLID|
|7.5|File write|`<home>/trusted.json` (0600/0700), written by `canny trust`|`canny/src/config.ts:80-84`|SOLID|
|7.6|File write|`<root>/.claude/settings.json` and `<root>/.codex/hooks.json`, via temp file + rename, by `init`/`remove`|`canny/src/install.ts:114-127`; `canny/src/cli.ts:129-133`|SOLID|
|7.7|stdout|The hook writes one JSON object; the other commands write console text|`canny/src/cli.ts:98`|SOLID|
|7.8|Subprocess|The only one: `execFileSync("git", ["check-ignore", "-q", path], {cwd, stdio:"ignore", timeout:2000})`. It runs only for a `.env`-shaped target when a secret matched. grep for `child_process\|execFile\|spawn` finds nothing else|`canny/src/checks.ts:178`|SOLID|
|7.9|Git invocations|Only `git check-ignore` (7.8). Every other `git` string in `src/` is parsed out of the agent's command text|`canny/src/events.ts:245-265`|SOLID|
|7.10|Env reads|`CANNY_JEV_MODEL`, `CANNY_JEV_URL` and `CANNY_JEV_TIMEOUT_MS` at module load; `TYPESAFE_API_KEY` on each call; `CANNY_HOME`; `PATH`, in `init` and in help messages; `HOME`, implicitly through `os.homedir()`|`canny/src/jev.ts:7-9, 88`; `canny/src/config.ts:22, 48`; `canny/src/cli.ts:104-105, 119, 154, 167`|SOLID|
|7.11|File reads (for completeness)|stdin; `.canny.json` and `trusted.json`; `CLAUDE.md`/`AGENTS.md`/`.claude/CLAUDE.md`; `package.json`, `justfile`, `Makefile`, `Cargo.toml`, `go.mod` (for the SessionStart hint); a test file from disk (Write damage); the tail of the Codex rollout; settings files (merge); ledgers and `errors.log` (status, replay)|`canny/src/checks.ts:99, 222`; `canny/src/config.ts:102`; `canny/src/rules.ts:25`; `canny/src/events.ts:450-458`; `canny/src/install.ts:75`; `canny/src/ledger.ts:110, 209, 220`; `canny/src/cli.ts:89`|SOLID|
|7.12|Install time: `prepare`|`git config --get core.hooksPath \|\| git config core.hooksPath .githooks \|\| true`. It runs on `pnpm install` in the Canny checkout and sets a repo-local `core.hooksPath=.githooks` when none is set|`canny/package.json:48`; `canny/CONTRIBUTING.md:30`|SOLID|
|7.13|Install time: `.githooks/pre-commit`|Runs `pnpm check`: format:check, type-check, lint, test:coverage, build, then `git diff --exit-code -- dist`|`canny/.githooks/pre-commit:4-7`; `canny/package.json:46`|SOLID|
|7.14|Install time: `prepack`|`pnpm build`|`canny/package.json:47`|SOLID|
|7.15|The user install path|The README's install is `git clone` then `node ~/.canny/src/dist/cli.js init`: "There is nothing to build or install." No `pnpm install` runs, so `prepare` does not run on this path|`canny/README.md:49, 57-58`|SOLID|
|7.16|Telemetry|None. grep for `telemetry\|analytics\|posthog\|sentry\|segment\|mixpanel\|otel\|opentelemetry\|beacon\|track\(` over `src/`, `dist/` and `package.json` has one hit: the word "segment" in a code comment ("once per command segment")|`canny/src/checks.ts:14`; `canny/dist/checks.js:10`|SOLID|
|7.17|The README's own list of what stays and what leaves (`canny/README.md:175-180`) agrees with 7.1-7.5: with a key set, clipped diffs, rules and the final message go to TypeSafe and are also cached on disk|as cited|—|SOLID|

## 8. Tests, CI and evidence of effect

### 8a. What each test file covers (call sites counted with `grep -cE '^\s*it\('` and `'^\s*it\.each'`; `it.each` expands to more cases; NOT run)

| # | File | `it` / `it.each` | Covers | Grade |
|---|---|---|---|---|
|8.1|`test/hook.test.ts`|33 / 5|The Stop gate (`:80-155`); shell file operations in the ledger (`:157-172`); pre checks (`:174-424`): secrets, including every secret shape through 11 routes into a file for both agents, the env-file exemption with `cd` variants, test removal through the shell, and repeat-failure note/deny; the rule check with a stub judge (`:426-521`); the pipefail rewrite table (`:523-578`); SessionStart records nothing (`:580-594`); serialize (`:596-606`); ledger file mode and escapes (`:608-630`); session lookup (`:632-670`); `hookErrors` (`:672-686`)|SOLID|
|8.2|`test/checks.test.ts`|13 / 6|`findSecrets` (`:16-31`); `isScratch`; an `isVerify` table of 27 rows (`:48-76`), plus a product of 11 checks × 14 forms that hide the exit status (none may count) and 11 checks × 13 wrappers that keep it (all must count) (`:80-131`); `config.verify` override; `isIgnored` (`pnpm-lock.yaml` → false, `:143`); `testDamage`; `fingerprint` (normalization; 200,000 digits under 1 s); `projectCheck` table|SOLID|
|8.3|`test/events.test.ts`|12 / 3|`normalize` for each tool; the PostToolUseFailure exit code; the Codex exit code from metadata or text; no exit code read from the middle of the output; Stop; `detectAgent`; `parsePatch`; the `writeTargets` and `fileOps` tables; the Codex rollout exit code; an unknown exit code → null|SOLID|
|8.4|`test/cli.test.ts`|8 / 0|Compiles `src/` with `pnpm exec tsc --outDir <tmp>` ("The committed `dist/` is not used") and runs each command as a process with a temp `HOME`/`CANNY_HOME`: init, hook JSON, status, sessions, replay, trust, remove, help, an unparseable settings file; a whole session going deny → block → warn → allow, replayed as 3 × ok, and an edited ledger → MISMATCH, exit 1; junk stdin → `{}` and one crash counted; `init --codex --global`|SOLID|
|8.5|`test/install.test.ts`|9 / 3|`isCannyHook` table; `hookConfig` matchers for every tool; `merge`: create, keep other settings, remove only Canny's entries, leave no empty `hooks`, keep odd entries, treat `null` hooks as none, refuse bad JSON (6 shapes), refuse to write through a planted temp symlink, follow a dangling symlink, keep the file mode|SOLID|
|8.6|`test/jev.test.ts`|4 / 0|No key → `null` and no fetch; parse + cache + both log paths, including the cached answer returned after the key is deleted; a cache write failure keeps the answer; HTTP 429 → `null` with the error logged|SOLID|
|8.7|`test/config.test.ts`|5 / 0|Untrusted weakening fields are dropped; a non-object file reads as `{}`; trust, and an edit that revokes it; a subdirectory; trust is keyed by path|SOLID|
|8.8|`test/rules.test.ts`|3 / 0|`extractRules` (bullets, continuations, fences); escape stripping; `loadRules` precedence, STRONG rules first, and `null` when nothing is found|SOLID|
|8.9|`test/ledger.test.ts`|1 / 1|Session-id sanitization (6 hostile ids); a torn line is skipped|SOLID|
|8.10|`test/robustness.test.ts`|1 / 1|Malformed payloads: 5 + 6 events × 8 tools × 8 junk values = 389 shapes, each must produce a decision; hostile text: 13 inputs × 10 parsers, each under 1 s|SOLID (count computed from the literal arrays)|
|8.11|`test/fixtures.test.ts`|0 / 1 (×2)|The recorded Claude Code and Codex sessions (`test/fixtures/*.jsonl`) against a snapshot. The last Stop is `block`, and the command exit codes are `[null, 3, null, 0]`|SOLID|
|8.12|`test/git-env.test.ts`|2 / 0|`GIT_*` env isolation: a test's `git init` must not re-initialize the real repository|SOLID|
|8.13|`test/bench.test.ts`|1 / 0|Runs `node bench/run.mjs` with stand-in agent commands, never a real agent. Untouched, every task fails; with the reference `solution.sh`, every task passes; the cheat (gutted tests + `scripts.test=true` + the key written into `notes.txt`) passes every task except `payment-key`|SOLID|
|8.14|`test/setup.ts`, `test/smoke.sh`|—|`setup.ts` deletes the `GIT_*` env vars and gives each test its own temp `CANNY_HOME`. `smoke.sh` copies only `dist/` and `package.json`, sets a temp `HOME`/`CANNY_HOME`, runs `init --claude`, runs the written hook command and `status`, once by path and once through a `canny` symlink|SOLID|
|8.15|Coverage gate|lines 97, statements 97, functions 96, branches 90; `src/cli.ts` is excluded from coverage|`canny/vitest.config.ts:8-15`|SOLID|

### 8b. CI

| # | Fact | Anchor | Grade |
|---|---|---|---|
|8.16|`ci.yml` triggers: push to main, pull requests, and Mondays 06:00 UTC. Permissions: `contents: read`|`canny/.github/workflows/ci.yml:3-17`|SOLID|
|8.17|`static` job (Node 24): format:check, type-check, lint, build, `git diff --exit-code -- dist`|`canny/.github/workflows/ci.yml:20-35`|SOLID|
|8.18|`test` job: Ubuntu with Node 22, 24 and 26, where the Node 24 cell runs coverage; macOS with Node 24|`canny/.github/workflows/ci.yml:37-63`|SOLID|
|8.19|`smoke` job: Ubuntu and macOS, Node 22, no `pnpm install`, runs `bash test/smoke.sh`. `ci-ok` passes only when static, test and smoke all passed|`canny/.github/workflows/ci.yml:65-89`|SOLID|
|8.20|`codeql.yml`: the `security-extended` queries, with `paths-ignore: dist, test`|`canny/.github/workflows/codeql.yml:19-35`|SOLID|
|8.21|Actions are pinned by major tag (`actions/checkout@v7`, `pnpm/action-setup@v6`, `actions/setup-node@v7`, `github/codeql-action/*@v4`), not by commit SHA|`canny/.github/workflows/ci.yml:24-26`; `canny/.github/workflows/codeql.yml:24-35`|SOLID|
|8.22|The CI run results at f2c5e53 were not fetched (no network). The README badge points at the workflow (`canny/README.md:5`)|—|UNSURE|

### 8c. The bench and the README's "Does it help?"

| # | Fact | Anchor | Grade |
|---|---|---|---|
|8.23|What `bench/run.mjs` does. Agent commands: `claude -p "$PROMPT" --output-format json --setting-sources project --permission-mode acceptEdits --allowedTools Bash Edit Write Read Glob Grep`, or `codex exec --skip-git-repo-check --dangerously-bypass-hook-trust -s workspace-write`. Each task is copied to a temp directory without `prompt.txt`, `solution.sh` and `check/`. A fresh `sk_test_…` key is generated per run. The directory gets `git init`, and the `canny` arm also gets `node dist/cli.js init`. The agent runs; then `test/` and `package.json` are restored from the task and `npm test` decides pass or fail. The row records turns, cost and API seconds from the Claude JSON, plus block, deny, note and rewrite counts from the run's own ledgers. The two arms alternate within each run|`canny/bench/run.mjs:45-50, 61-119, 121-155`|SOLID|
|8.24|Five tasks: `csv-export-regression` ("`npm test` went red after yesterday's refactor"), `payment-key` (a key handed over in the prompt; `check/secret.test.js` fails if the key is in any committable file, the index or history), `percentile-report` (the tests are the spec), `rename-session-field` (4 modules), `slug-keep-underscores` (a test has to change; judged by `check/`)|`canny/bench/tasks/*/prompt.txt:1`; `canny/bench/tasks/payment-key/check/secret.test.js:9-22`|SOLID|
|8.25|The README's numbers, verbatim: "With Opus 5 and Sonnet 5 on Claude Code, every run passed in both arms"; "The Canny arm took 4.5 seconds longer per task with Opus 5, and 6.8 with Sonnet 5"; "a 25-pair Opus 5 run (Claude Code 2.1.278) had no blocks, 25 of 25 passes in both arms, the same number of turns and the same cost, and the Canny arm 1.6 ± 3.4 seconds faster"; pi-warden's external "A/B run of 4 versus 3 rule violations". The CHANGELOG repeats the 25-pair figure|`canny/README.md:245`; `canny/CHANGELOG.md:15`|SOLID (as quotes)|
|8.26|The repo does NOT carry the data behind 8.25. `bench/results/` is gitignored (`canny/.gitignore:9-10`), `ls bench/` shows only `run.mjs` and `tasks/`, and `git ls-files` lists no result `.jsonl`|as cited|SOLID (the absence is proven over the full tracked list)|
|8.27|The README's own framing: "Whether it improves an agent's work over a whole project has not been measured yet … the bench shows no change in outcome yet"|`canny/README.md:245`|SOLID (as a quote)|
|8.28|"One hook call costs about 40 milliseconds on a laptop." (`canny/README.md:182`). A repo-wide grep for `40 ?(ms\|milli)` finds only this line; no committed measurement produces it|as cited|UNSURE (a claim with no producer)|

## 9. `dist/` against `src/`

| # | Fact | Anchor | Grade |
|---|---|---|---|
|9.1|Method, with no build. (a) I read all nine src/dist pairs in full. (b) `cmp.py` tokenized both trees and diffed the ordered sequences of string, template, regex and number literals, and separately of comments. (c) `ops.py` counted the operators `===`, `!==`, `>=`, `<=`, `&&`, `\|\|`, `??`, `?.`, `++`, `--`, `+=`, `**` outside literals and comments|scratchpad `canny/cmp.py`, `canny/ops.py`|SOLID|
|9.2|The literal and comment diff has 54 lines in total, all on the `src` side. They are: `import type` module paths (`"./config.js"`, `"./events.js"`, `"./jev.js"`); TypeScript literal types (`"claude"`, `"codex"`, the phase names, the event and decision kinds, `"noul"`, `"criteria"`); the `as "sed" \| "perl"` cast; and JSDoc comments on interface and type members. No line exists only on the `dist` side. The literals and comments of `cli` and `install` are identical|`cmp.py` output|SOLID|
|9.3|The operator counts are equal for checks, jev, ledger and rules. The only differences are in `>=` (src/dist: cli 1/0, config 1/0, events 4/3, hook 4/3, install 1/0). Each extra `>=` in `src` is a generic type closing before `=` or `=>` (`Record<…> =`, `Record<…> =>`), at `canny/src/cli.ts:87`, `config.ts:88`, `events.ts:58`, `hook.ts:338` and `install.ts:89`. All 8 real comparisons appear in both trees|grep of `>=` in `src/*.ts` and `dist/*.js`|SOLID|
|9.4|Result: this method found no file whose logic visibly differs between `dist/` and `src/`|9.1-9.3|SOLID (static comparison; no build)|
|9.5|The guards on this in the repo: CI's `static` job builds and then runs `git diff --exit-code -- dist` (`canny/.github/workflows/ci.yml:34-35`); `pnpm check` and the pre-commit hook do the same (`canny/package.json:46`; `canny/.githooks/pre-commit:4`). The CI outcome at f2c5e53 is not known here|as cited|UNSURE (the CI outcome)|
|9.6|`dist/cli.js` is the only executable file (mode 755) and starts with `#!/usr/bin/env node`. The package `bin` is `dist/cli.js`, and `files` = `dist`, `README.md`|`ls -la dist/`; `canny/dist/cli.js:1`; `canny/package.json:27-33`|SOLID|
|9.7|The tests do not use `dist/`: `cli.test.ts` compiles `src/`, and the other tests import `src/`. Only `test/smoke.sh`, in the CI smoke job, runs `dist/`|`canny/test/cli.test.ts:14-15, 29-35`; `canny/test/smoke.sh:13`; `canny/.github/workflows/ci.yml:65-79`|SOLID|

## 10. Our side (af): quoted, not interpreted

| # | Fact (quoted) | Anchor | Grade |
|---|---|---|---|
|10.1|J1 goal: "Build increment J1 of agent-factory — the PASSIVE decision ledger of the Jev/Laya advisory layer — as a committed, test-gated module plus the J0 probe contract, with no model, no service, no hook seam, and no consumer."|`af/seeds/seed-laya-j1-v1.yaml:13-15`|SOLID|
|10.2|J1 constraints: "Ledger-first: J1 ships a passive decision ledger only — no model, no service, no hook seam, no consumer" (`:79-80`); "Laya is ADVISORY forever — never a term in any gate, lint, commit, push, or proof predicate (STANDING PROJECT RULE 12)" (`:81-82`); "The advisory-exclusion rule is mechanized by scripts/no_laya_in_gates.py wired into pre-commit, not left to prose" (`:83-84`); "Harvest reads only committed sources; replaying the same committed sources twice must produce the identical ledger" (`:94-95`); "No LLM judge anywhere in the ledger, canonicalization, or screen spine" (`:98`)|`af/seeds/seed-laya-j1-v1.yaml:79-99`|SOLID|
|10.3|The J1 row fields: row_id, row_type, state, state_digest, incumbent_answer, source_kind, source_ref, redactions, captured_only (`:183-227`). An evaluation principle: "Replay determinism — Harvesting the same committed sources twice produces a byte-identical ledger; identity and digests do not drift with commit SHA, timestamps, or transcript compaction" (`:229-233`)|`af/seeds/seed-laya-j1-v1.yaml:177-233`|SOLID|
|10.4|Pinned decisions in the J1 breakdown: "Row = one incumbent decision, never a bare question." (`:13`); "row_id = sha256(canonical JSON of {producer, question_id, state_digest, source_ref})" (`:14`); "Duplicate append is a NAMED refusal `decision-row-duplicate: <row_id>`" (`:15`); "state = a BOUNDED, CLOSED, per-question-type extraction; never verbatim bytes." (`:16`); "Order of transforms: normalize → redact → canonical → sha256." (`:17`); "Mandatory provenance per row" (`:18`); "Harvest reads only COMMITTED sources through STRICT grammars" (`:19`)|`af/tasks/laya-j1-breakdown.md:13-19`|SOLID|
|10.5|J1-2: "`ledger.py`: append-only JSONL writer, mandatory provenance, row_id, duplicate refusal, replay reader with digest verification" (`:31`). NOT built: "No service, no sieve, no hook seam, no consumer, no Laya call anywhere in J1" (`:39-40`)|`af/tasks/laya-j1-breakdown.md:31, 39-40`|SOLID|
|10.6|KC-J1: "gate reachability (absorbing barrier, no threshold to retune). If `scripts/no_laya_in_gates.py` reports any Laya/System-One vocabulary (`laya`, `systemone`, `system_one`, `decide ask`, `sieve`, `jev`) inside a gate-defining file, or a Laya value is shown reachable from a gate/merge/lint/commit/push/proof predicate, at any time after the screen lands (due 2026-10-06) — the verdict is invalidated and we pull the layer, revert the integration, and regenerate every dependent attested artifact". KC-J1b: "A Laya score must never be the sole evidence for an ANTI-PATTERN REGISTRY row … nor for a verifier per-finding class"|`af/docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md:45-46`|SOLID|
|10.7|The screen's docstring: "Advisory-exclusion screen: no Laya/Jev vocabulary in gate-defining files. KC-J1 mechanism -- an absorbing barrier with no bypass." Exit codes: "0 clean · 3 violation (one line per hit: <path>:<line>:<token>) · 4 completeness control (gate-file-unlisted, gate-file-missing, gate-file-not-regular or gate-file-unreadable) · 64 usage error". The closed vocabulary: `SIMPLE_TOKENS` = laya, systemone, system_one, system-one, jev, jevcache, sieve, sieve-run, decide-harvest, decide_harvest, laya-decide (`:32-36`); `DOTTED_TOKENS` = agent_factory.decisions, decisions.ledger, decisions.canonical, decisions.jsonl (`:39-44`). The breakdown gives the scanned set: the `scripts/gate_files.txt` allowlist plus a completeness walk (`af/tasks/laya-j1-breakdown.md:20`)|`af/scripts/no_laya_in_gates.py:2-10, 32-44`|SOLID|
|10.8|Our Stop hook. `af/.claude/settings.json:61-70` → `bash $CLAUDE_PROJECT_DIR/.claude/hooks/turn-retro-gate.sh`. The script fires once per new HEAD (sentinel `<git-dir>/turn-retro-acked`, `:12-17`), exempts index-stamp churn and wiki-only commits (`:18-38`), prints a 5-item retro checklist to stderr and runs `exit 2` (`:47-55`). The user-scope `~/.claude/settings.json` registers no Stop hook (its hook events: PostToolUse, PreToolUse, SessionStart, SubagentStart). Of the enabled plugins, honey registers SessionStart, SubagentStart and PostToolUse(Bash), and aegis registers SessionStart; neither registers a Stop hook|`af/.claude/hooks/turn-retro-gate.sh:12-55`; `~/.claude/plugins/cache/greenpt/honey/1.3.1/hooks/hooks.json`|SOLID|
|10.9|Our other project hooks: SessionStart session-start.sh; PostToolUse `Edit\|Write\|Read` → edit-snapshot.py; UserPromptSubmit → wiki-context.py; PreToolUse `Grep` → graft-first-nag.py|`af/.claude/settings.json:29-81`|SOLID|
|10.10|The installed plugins, at user scope. `aegis@aegis-dev` 2.10.6 @ 60321ed, from the source directory `/root/jev-plugins/Aegis` (a shallow clone; HEAD 2026-09-20 19:25:26 +0800). `fast-jev-output@fast-jev-output` 0.1.0 @ 47d017c, from `/root/jev-plugins/jev-pruner` (a shallow clone; HEAD 2026-09-19 10:18:30 +0000). Both are true in `enabledPlugins` in `~/.claude/settings.json`|`~/.claude/plugins/installed_plugins.json:14-33`; `~/.claude/plugins/known_marketplaces.json:10-25`|SOLID|
|10.11|aegis hooks: SessionStart only, with matcher `startup\|clear\|compact`, running `run-hook.cmd session-start`|`~/.claude/plugins/cache/aegis-dev/aegis/2.10.6/hooks/hooks.json:1-16`|SOLID|
|10.12|fast-jev-output hooks: `{ "modules": ["./fast-jev-output.ts"] }`, with one registration, `on('tool.call', { tool: 'Bash' }, …)`|`~/.claude/plugins/cache/fast-jev-output/fast-jev-output/0.1.0/hooks/hooks.json:1`; `…/hooks/fast-jev-output.ts:153`|SOLID|
|10.13|A local patch. The source clone has uncommitted changes (`M .claude-plugin/plugin.json`, `M hooks/fast-jev-output.ts`; +11/-2). They add a `baseUrl` userConfig, described as "Overrides https://api.typesafe.ai/v1/systemone (e.g. the local Laya server scripts/laya_systemone_server.py in agent-factory)", and pass it through to `buildJevRequest`. `diff -rq` of the clone against the installed cache shows no differences. The patch and install are recorded in the ledger|`/root/jev-plugins/jev-pruner` `git diff`; `…/0.1.0/.claude-plugin/plugin.json:73-77`; `af/todo/BUILD-TASKLIST.md:162`|SOLID|
|10.14|`~/.claude/settings.json` holds `env.CLAUDE_CODE_ENABLE_FUNCTION_HOOKS = "1"`. Its `pluginConfigs["fast-jev-output@fast-jev-output"]` has one option name, `baseUrl`, with the value `http://127.0.0.1:47411/v1/systemone` (read 2026-09-23; no secret value is printed here). `TYPESAFE_API_KEY` and `CANNY_*` are not set in this shell (names checked only)|`~/.claude/settings.json`|SOLID|
|10.15|The prior audit's §7, quoted: "1. **No model judge in the gate spine** … A System One judgment prunes, ranks, triages and routes; it never decides a green, a mint, a verdict or a ledger row. A wrong judgment must be recoverable" (`:160-162`); "2. **Rule 3:** the hosted TypeSafe API and `TYPESAFE_API_KEY` are not production dependencies. The backend is the self-hosted Laya." (`:163-165`); "3. **Rule 13 / S0-12:** every upstream pinned by commit or digest in `upstream.lock.yaml`" (`:166-167`); "4. **Rule 11:** the decide service binds loopback (sandbox) or the bridge/tunnel with a token (PC); no new egress." (`:168`); "5. **Errors are never hidden**" (`:169-170`); "6. **The deterministic digest, not an LLM summary, is the default stub**" (`:171-172`); "7. **Everything measured before it hides anything**" (`:173-174`)|`af/docs/research/findings/JEV-LAYA-AUDIT-2026-09-22.md:158-174`|SOLID|
|10.16|The prior audit's §8, quoted: "A. The sandbox tool-output sieve." (`:178-180`); "B. The Hermes-lane sieve … behind a `terminal` command wrapper, wired by the `pre_tool_call` MODIFY seam" (`:181-184`); "C. Relevance ranking for injected context." (`:185-186`); "D. Typed-decision constants in skills." (`:187-189`); "E. Bounded: the code-intel quartet." (`:190-191`); "F. Excluded: every T3 gate; the dispatcher's lane-state regexes; anything that writes a ledger, a mint, a verdict or a report class." (`:192-193`)|`af/docs/research/findings/JEV-LAYA-AUDIT-2026-09-22.md:176-193`|SOLID|

## Contradictions recorded (both sides cited in the rows; not resolved)

- 1.22: the README lists the repeat-failure deny under PostToolUse; the code emits it from PreToolUse.
- 1.26: the README says the test-removal reason explains how to allow the removal in `.canny.json`; no such text is in the reason strings.
- 1.27: the flowchart has no `warn` branch; the code and the prose have one.
- 2.15: the README says lockfiles do not count as code; `pnpm-lock.yaml` counts (code and test).
- 2.19: the deny text says to change the code first; the failure count never resets within a session.
- 2.24: the README's `password = "…"` wording; the code also matches the names api_key, secret and token.
- 3.29: the README says that with the key unset the judgment questions go unanswered; cached answers are returned without a key (code and test).
- 3.30: the README says every call is logged; the no-key path returns before logging.
- 3.31: the README says "above 0.9" / "below 0.1"; the code compares inclusively.
- 4.9: the README says every hook event is written and file contents never are; SessionStart and allowed PreToolUse events are not written, and heredoc bodies are stored inside `command`.
- 5.9: the README says a failed Codex transcript lookup leaves the exit code unknown; the code falls back to the output text.
- 6.5: the README says `canny trust` lands in the ledger; `trust` writes only `trusted.json`.
- 6.9: the README says `CANNY_HOME` holds the source checkout; no code reads a checkout under it.

## UNSURE / not determined

- Nothing from the clone was executed: no build, no test, no hook run, no replay, no Jev call. Every behavioral statement above is read from source.
- Per-file chronology of the Canny repo: UNAVAILABLE (shallow clone, one commit).
- Whether Claude Code and codex-cli honor Canny's output JSON at their current versions (5.6, 5.12). Claude Code's "caps consecutive blocks at eight" (2.5) is external and unverified.
- Whether concurrent `appendFileSync` calls from parallel hook processes stay whole lines (4.5). The code has no lock, and the reader tolerates torn lines.
- The CI outcome at f2c5e53 (8.22, 9.5): not fetched, no network.
- The README's "Does it help?" numbers (8.25) and "about 40 milliseconds" (8.28): no committed data produces them.
- What Laya answers for Canny's multi-rule, single-state request (3.21), and the latency of such a request against the 3,000 ms default (3.20): NOT measured. Canny against our endpoint was NOT run. From code, Canny sends nothing unless `TYPESAFE_API_KEY` is non-empty (3.15).
- How `AbortSignal.timeout` behaves when `CANNY_JEV_TIMEOUT_MS` is not a number (`Number(...)` → NaN, `canny/src/jev.ts:9`): not determined. The call sits inside the `try` at `:91-101`.
- The exit status when the hook's own error-log write throws (1.29): not determined.
- Hermes's per-event contract (5.18) is quoted from our adapter's docstring (569914b). The Hermes source was not re-read in this lane. `af/harness-ports/tests/test_hermes_spool.py`, cited by `af/harness-ports/hermes/config-snippet.yaml:152-153`, was not read.
- The origin of the Claude-path `baseUrl` patch is known only from the ledger line (10.13). `af/harness-ports/bin/jev-pruner-setup.sh` (untracked) patches only the Codex path, with `JEV_BASE_URL` (line 37); a grep for `plugin.json` or `fast-jev-output.ts` in it finds nothing.
