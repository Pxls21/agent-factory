# Provenance: vendor/jev-pruner

- **Upstream:** https://github.com/tamaratran/jev-pruner (package `fast-jev-output` 0.1.0)
- **Pin:** commit `47d017c34eab7690b95f075ce6f4839247c5dc0a` (2026-09-19 10:18:30 +0000, "Merge pull request #64")
- **License:** MIT (`LICENSE`, copied verbatim; sha256 `06dcddbb6908a0c6dd4a9e8ec822eea41d5a460a53089fecccc8a68049e99241`)
- **Pinned in:** `upstream.lock.yaml` `advisory_tooling.jev-pruner`; registered as a vendored root in
  `scripts/vendored_manifest.py` (`VENDORED_ROOTS`) and `sandbox-kit/VENDORED-FROM.md`.
- **Vendored:** 2026-09-25 by the P1 build lane (task #231, seed `seeds/seed-jev-pipes-p1-v1.yaml`, D-087).
- **Changed:** 2026-09-30 by the T408 build lane (task #408, D-118 item 2): local change 2 (the floor as a hook option)
  and the plugin manifests, so the copy installs as a plugin of its own (below); 2026-10-01 by the coordinator: local
  change 3 (task #415) and local change 4 with the version 0.1.1 (task #436).
- **Role:** advisory. The replay harness `scripts/jev_pipes/replay_pruner.py` runs this copy's own chunking, keep rules and
  rendering. It is never a gate and never sits in a fail-closed path.

## What was copied, and how

The source was the owner's local checkout `/root/jev-plugins/jev-pruner` (origin `https://github.com/tamaratran/jev-pruner`),
read only. The copy came from the COMMIT OBJECT, never the working tree:

```
git -C /root/jev-plugins/jev-pruner archive 47d017c src hooks package.json LICENSE README.md tsconfig.json | tar -x -C vendor/jev-pruner
```

The checkout's working tree was dirty at vendoring time: `.claude-plugin/plugin.json` and `hooks/fast-jev-output.ts` carried an
uncommitted `baseUrl` patch (the owner's pointer at the local Laya server). That patch is NOT vendored: `hooks/` here is the
commit's version (plus local change 2 since 2026-09-30, below). The replay does not need it, because `buildJevRequest` in
`src/jev.ts` already takes `baseUrl` at the commit.

Copied: `src/`, `hooks/`, `package.json`, `LICENSE`, `README.md`, `tsconfig.json` (kept so a reader can rebuild `dist/`),
and `dist/` (below). Not copied: `node_modules/` (the package has no runtime `dependencies`; its `devDependencies` are
TypeScript, `tsx`, `vitest` and `@types/node`), `tests/`, `evals/`, `types/`, `demo/`, `codex/`, `.claude-plugin/`
(added 2026-09-30, below), `.codex-plugin/`, `.agents/`. `README.md` is upstream's, verbatim: it still says the floor is
10,000 tokens, which holds here only while `minTokensFloor` is unset.

## Added 2026-09-30: the plugin manifests (T408)

`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` came from the same commit object, one file at a time
(`git -C /root/jev-plugins/jev-pruner show 47d017c34eab7690b95f075ce6f4839247c5dc0a:<path>`), then took the local changes
below. The installed plugin (`/root/.claude/plugins/cache/fast-jev-output/fast-jev-output/0.1.0/`) carries the owner's
uncommitted `baseUrl` patch in `plugin.json` and in the hook; it is not copied.

| File | upstream git blob at 47d017c | sha256 here |
|---|---|---|
| `.claude-plugin/plugin.json` | `db3a0b1ed98aaae664a4c2ac8c5143c9d2c0b3d6` | `801d2d6109ac2b12827f34d3138c32259b33626a129a50afbd4bb51e99c455ae` (change 4; `06e7e2c7…` after change 3, `f1f83c08…` after T408) |
| `.claude-plugin/marketplace.json` | `6b3748fc216ab50a65eccdbbad4197dd2b2a147b` | `d7520ca6a8719e3e4308ac0bdf078683a2d4f42478e0df4a51ec012fe1295e1e` (change 4's version; `486e2105…` before) |
| `hooks/hooks.json` (copied 2026-09-25, unchanged) | `b929bab3cdf8e42c2f8b9abcd6ef27a438ab0e52` | `f880049cfcf59ed9f324e6440ac1b924602945141b0925820d968403c767f240` |

The plugin needs no other file to load. `claude plugin validate` (Claude Code 2.1.285, run under `unshare --net` on scratch
copies of the commit) follows the hook's imports: `plugin.json`, `hooks/hooks.json`, `hooks/fast-jev-output.ts` and
`src/{jev,output,history,retention,secrets}.ts` pass; without `src/history.ts` it reports `cannot import "./history.js"` (since change 4 the hook's own import:
`cannot import "../src/history.js" (from hooks/fast-jev-output.ts)`);
without `package.json` it still passes. Still not copied: `types/` and `tsconfig.hooks.json` (they type-check the hook,
`npm run typecheck:hooks`; its `claude-code` import is type-only and empty at run time), `.codex-plugin/`, `codex/`,
`.agents/`, `tests/`, `evals/`, `demo/`, `package-lock.json`, `.gitignore`, `node_modules/`.

### Installing it (the coordinator's step; the T408 lane ran none of it)

The copy is its own local marketplace, the way `scripts/setup.sh` installs honey from `sandbox-kit/honey-for-devs/`:
`.claude-plugin/marketplace.json` lists one plugin whose source is this directory (`"./"`). Both names differ from the
owner's `fast-jev-output@fast-jev-output`, so the two can be installed side by side: the marketplace is
`agent-factory-vendor` (this repository's vendored plugins) and the plugin is `fast-jev-output-floor` (upstream's name and
what this copy adds). The rest of both manifests is upstream's, the marketplace `owner` included (the plugin's author).

```
claude plugin marketplace add /home/user/agent-factory/vendor/jev-pruner
claude plugin install fast-jev-output-floor@agent-factory-vendor --config minTokensFloor=<F> --config minTokens=<M>
```

Both hooks wrap the same Bash tool call and archive under the same `.claude/fast-jev-output/`, so enable one of the two
plugins at a time.

## dist/ is a build, not an upstream file

Upstream ignores `dist` (`.gitignore` at 47d017c), so the commit has no `dist/`. It was built here with TypeScript 5.9.3 (the
version `package-lock.json` pins at 47d017c) from the commit's `src/` and `tsconfig.json`:

```
node node_modules/typescript/bin/tsc -p tsconfig.json
```

That pinned build (44 files) was byte-identical (`diff -r`, no output) to the `dist/` of the installed plugin
(`/root/jev-plugins/jev-pruner/dist`, built there 2026-09-22 19:17). After the local change below, `dist/` was rebuilt the
same way from the changed `src/`. Only four files differ from the pinned build: `dist/output.js` and `dist/output.d.ts`
(diffs below) and their two source maps (regenerated by the compiler):

| File | sha256 of the pinned build | sha256 here |
|---|---|---|
| `dist/output.js.map` | `4f8b55191be8ca8cfe6e5153ee841643e2bebbb6f9496ab4f90235fe93f9ce2f` | `28af6f2d38062daf7fa6d71b29673b0579935e2b50d795c9342c804602304711` |
| `dist/output.d.ts.map` | `d5ee78a98c36aa32eb97de0bf083dd97b82f4f9dd8f7adf88efb83aa13dc9668` | `458d0dc1e8f76196e325d07e4af077d4c2b8c5b045ed635e6e1b12d1f4238ee5` |

## Local changes (every one, as a diff)

There are FOUR local changes, plus the manifests' own (below). The first two lower the output-size floor only when
asked; the third adds three options (the scorer's URL, the archive folder, the decision records), each off when unset;
the fourth adds one (the history window, off when unset) and raises the copy's version.

Change 1 (P1, task #231, 2026-09-25) is an explicit option for LIBRARY callers. Upstream floors `minTokens` at
`MIN_OUTPUT_TOKENS = 10_000` in `exceedsOutputThreshold` (`src/output.ts:81-83` at 47d017c), so a caller cannot trim anything
smaller. The new option `minTokensFloor` replaces that floor ONLY when a caller passes it. Without it the arithmetic is the
upstream one: `Math.max(10_000, finite(minTokens, 10_000))`. A non-finite value falls back to the default floor; a negative
value clamps to 0. Every upstream caller (`src/output.ts` `trimOutputAttempt`, `src/codex/prune.ts:25`,
`hooks/fast-jev-output.ts:178` at 47d017c) behaved as before; only `trimOutputAttempt` forwarded the new option (change 2
makes the hook pass it too).
`tests/test_jev_pipes_replay.py` holds the default: a 9,999-token output still passes untouched without the option.

### src/output.ts

```diff
--- a/src/output.ts
+++ b/src/output.ts
@@ -26,6 +26,11 @@
 
 export interface TrimOutputOptions {
   minTokens?: number;
+  /**
+   * agent-factory local change (vendor/jev-pruner/PROVENANCE.md): the floor under
+   * minTokens. Default MIN_OUTPUT_TOKENS; only a caller that passes it lowers it.
+   */
+  minTokensFloor?: number;
   chunkLines?: number;
   /** Optional character target instead of line grouping; 0 uses chunkLines. */
   chunkChars?: number;
@@ -78,8 +83,9 @@
   return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
 }
 
-export function exceedsOutputThreshold(output: string, minTokens?: number): boolean {
-  return estimateTokens(output) > Math.max(MIN_OUTPUT_TOKENS, finite(minTokens, MIN_OUTPUT_TOKENS));
+export function exceedsOutputThreshold(output: string, minTokens?: number, minTokensFloor?: number): boolean {
+  const floor = Math.max(0, finite(minTokensFloor, MIN_OUTPUT_TOKENS));
+  return estimateTokens(output) > Math.max(floor, finite(minTokens, floor));
 }
 
 /** Output with NULs or a lot of control bytes is not text worth chunking. */
@@ -383,7 +389,7 @@
     finite(options.maxStateTokens, DEFAULT_MAX_STATE_TOKENS),
   );
 
-  if (!exceedsOutputThreshold(input.output, options.minTokens)) return untrimmed(input.output, 0, [], 'below_threshold', options.onDecision);
+  if (!exceedsOutputThreshold(input.output, options.minTokens, options.minTokensFloor)) return untrimmed(input.output, 0, [], 'below_threshold', options.onDecision);
 
   if (looksBinary(input.output)) return untrimmed(input.output, 0, [], 'binary', options.onDecision);
   const category = classifyOutput(input.command, input.output);
```

### dist/output.js

```diff
--- a/dist/output.js
+++ b/dist/output.js
@@ -17,8 +17,9 @@
 function finite(value, fallback) {
     return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
 }
-export function exceedsOutputThreshold(output, minTokens) {
-    return estimateTokens(output) > Math.max(MIN_OUTPUT_TOKENS, finite(minTokens, MIN_OUTPUT_TOKENS));
+export function exceedsOutputThreshold(output, minTokens, minTokensFloor) {
+    const floor = Math.max(0, finite(minTokensFloor, MIN_OUTPUT_TOKENS));
+    return estimateTokens(output) > Math.max(floor, finite(minTokens, floor));
 }
 /** Output with NULs or a lot of control bytes is not text worth chunking. */
 export function looksBinary(output) {
@@ -273,7 +274,7 @@
     const chunkLines = Math.max(1, Math.floor(finite(options.chunkLines, DEFAULT_CHUNK_LINES)));
     const keepThreshold = finite(options.keepThreshold, DEFAULT_KEEP_THRESHOLD);
     const maxStateTokens = Math.max(1, finite(options.maxStateTokens, DEFAULT_MAX_STATE_TOKENS));
-    if (!exceedsOutputThreshold(input.output, options.minTokens))
+    if (!exceedsOutputThreshold(input.output, options.minTokens, options.minTokensFloor))
         return untrimmed(input.output, 0, [], 'below_threshold', options.onDecision);
     if (looksBinary(input.output))
         return untrimmed(input.output, 0, [], 'binary', options.onDecision);
```

### dist/output.d.ts

```diff
--- a/dist/output.d.ts
+++ b/dist/output.d.ts
@@ -5,6 +5,11 @@
 export type TrimDecision = 'below_threshold' | 'binary' | 'document' | 'few_chunks' | 'no_scoring_capacity' | 'budget_unfit' | 'incomplete_coverage' | 'kept_all' | 'pruned';
 export interface TrimOutputOptions {
     minTokens?: number;
+    /**
+     * agent-factory local change (vendor/jev-pruner/PROVENANCE.md): the floor under
+     * minTokens. Default MIN_OUTPUT_TOKENS; only a caller that passes it lowers it.
+     */
+    minTokensFloor?: number;
     chunkLines?: number;
     /** Optional character target instead of line grouping; 0 uses chunkLines. */
     chunkChars?: number;
@@ -38,7 +43,7 @@
     charsAfter: number;
     scores: number[];
 }
-export declare function exceedsOutputThreshold(output: string, minTokens?: number): boolean;
+export declare function exceedsOutputThreshold(output: string, minTokens?: number, minTokensFloor?: number): boolean;
 /** Output with NULs or a lot of control bytes is not text worth chunking. */
 export declare function looksBinary(output: string): boolean;
 /**
```

### Change 2: hooks/fast-jev-output.ts (T408, task #408, D-118 item 2, 2026-09-30)

Change 2 makes the floor a plugin option. The hook reads `minTokensFloor`: a finite number of at least 0, default
`MIN_OUTPUT_TOKENS`, so with no option the behavior is upstream's exactly. A value that is not a finite number of at least 0
(NaN, Infinity, -Infinity, a negative number, a non-number) falls back to `MIN_OUTPUT_TOKENS`: a bad value never lowers
the floor. This differs on purpose from change 1's library rule (a negative value clamps to 0); the library never sees
such a value from the hook, which resolves the floor first. `minTokens` is clamped to the resolved floor, and the floor
goes to both gates, the hook's own `exceedsOutputThreshold` call and `trimOutput`'s (through its options), so the two
agree. The threshold is `max(minTokensFloor, minTokens)`, and `minTokens` still defaults to 10000 (the manifest fills it
in), so a lower floor alone changes nothing: set `minTokens` too. `tests/test_jev_pruner_floor.py` drives the real module
through its exports. No `src/` file changed, so `dist/` was not rebuilt.

```diff
--- a/hooks/fast-jev-output.ts
+++ b/hooks/fast-jev-output.ts
@@ -53,6 +53,7 @@
   maxStateTokens: number;
   maxScoringRequests?: number;
   minTokens: number;
+  minTokensFloor: number;
   persistedOutputs: boolean;
   persistedMaxChars: number;
   model: string;
@@ -69,11 +70,16 @@
 }
 
 export function resolveHookConfig(options: PluginOptions): HookConfig {
+  // agent-factory local change (vendor/jev-pruner/PROVENANCE.md): the floor under minTokens is an option. A value that
+  // is not a finite number of at least 0 falls back to MIN_OUTPUT_TOKENS, so a bad value never lowers the floor.
+  const floor = optionNumber(options, 'minTokensFloor', MIN_OUTPUT_TOKENS);
+  const minTokensFloor = floor >= 0 ? floor : MIN_OUTPUT_TOKENS;
   const config: HookConfig = {
     chunkLines: optionNumber(options, 'chunkLines', DEFAULTS.chunkLines),
     keepThreshold: optionNumber(options, 'keepThreshold', DEFAULTS.keepThreshold),
     maxStateTokens: optionNumber(options, 'maxStateTokens', DEFAULTS.maxStateTokens),
-    minTokens: Math.max(MIN_OUTPUT_TOKENS, optionNumber(options, 'minTokens', DEFAULTS.minTokens)),
+    minTokens: Math.max(minTokensFloor, optionNumber(options, 'minTokens', DEFAULTS.minTokens)),
+    minTokensFloor,
     persistedOutputs:
       typeof options.persistedOutputs === 'boolean' ? options.persistedOutputs : true,
     persistedMaxChars: optionNumber(options, 'persistedMaxChars', DEFAULTS.persistedMaxChars),
@@ -175,7 +181,7 @@
       sourceChars = output.length;
       if (configured.diagnostics) sourceEstimatedTokens = estimateTokens(output);
       decision = 'below_threshold';
-      if (!exceedsOutputThreshold(output, configured.minTokens)) return answer;
+      if (!exceedsOutputThreshold(output, configured.minTokens, configured.minTokensFloor)) return answer;
       decision = 'binary';
       if (looksBinary(output)) return answer;
       informationCategory = classifyInformation(output);
@@ -238,6 +244,7 @@
         ),
         {
           minTokens: configured.minTokens,
+          minTokensFloor: configured.minTokensFloor,
           maxChars: Number.isFinite(maxChars) ? maxChars : 0,
           compactMarkers: true,
           chunkLines: configured.chunkLines,
```

### .claude-plugin/plugin.json

The plugin is renamed (above), `minTokensFloor` is declared, and the `minTokens` description no longer says the minimum is
10000. The bound is the schema's `min` key: `claude plugin validate` refuses `minimum` (`Unrecognized key: "minimum"`),
and the CLI checks a stored value against `min` (`<title> must be at least <min>`).

```diff
--- a/.claude-plugin/plugin.json
+++ b/.claude-plugin/plugin.json
@@ -1,5 +1,5 @@
 {
-  "name": "fast-jev-output",
+  "name": "fast-jev-output-floor",
   "version": "0.1.0",
   "description": "Trim long Bash output with Jev before the model sees it (Claude Code plugin)",
   "license": "MIT",
@@ -13,9 +13,16 @@
     "minTokens": {
       "type": "number",
       "title": "Minimum Bash output tokens",
-      "description": "Stdout at or below this estimated token count passes through untouched. Minimum: 10000.",
+      "description": "Stdout at or below this estimated token count passes through untouched. Minimum: the minTokensFloor option (default 10000).",
       "default": 10000
     },
+    "minTokensFloor": {
+      "type": "number",
+      "title": "Floor under the minimum Bash output tokens",
+      "description": "Lowest value minTokens can take; upstream fixes it at 10000 (agent-factory local option, vendor/jev-pruner/PROVENANCE.md). Lowering it changes nothing unless minTokens is lowered too. A value below 0 or not finite counts as 10000.",
+      "default": 10000,
+      "min": 0
+    },
     "persistedOutputs": {
       "type": "boolean",
       "title": "Prune output the engine saved",
```

### .claude-plugin/marketplace.json

```diff
--- a/.claude-plugin/marketplace.json
+++ b/.claude-plugin/marketplace.json
@@ -1,12 +1,12 @@
 {
-  "name": "fast-jev-output",
+  "name": "agent-factory-vendor",
   "owner": {
     "name": "tamaratran",
     "url": "https://github.com/tamaratran"
   },
   "plugins": [
     {
-      "name": "fast-jev-output",
+      "name": "fast-jev-output-floor",
       "source": "./",
       "description": "Trim long Bash output with Jev before the model sees it (Claude Code plugin)",
       "version": "0.1.0",
```

### Change 3: the scorer's URL, the archive folder and the decision records (task #415, D-123 item 1, 2026-10-01)

Three string options, each unset by default, so with none of them the behavior is upstream's (and change 2's) exactly.

- `baseUrl`: the URL the hook sends Jev requests to (`buildJevRequest` in `src/jev.ts` already takes it at the commit; the
  hook never passed it). This ports the owner's uncommitted patch in the installed plugin (`HookConfig.baseUrl`, read by
  `optionString`, passed through `jevAsker`), written here from its lines, which the coordinator read on 2026-10-01 with the
  owner's leave (D-123 item 1). Its manifest entry is new text, not the installed one.
- `archiveDir`: where a trimmed output's full text is saved for recovery (upstream: `.claude/fast-jev-output`). Under
  `.claude/` the archive drifts this repository's vendored-tree manifest (it hashes ignored files there; task #232), so the
  install points it under `.jev/`.
- `decisionsDir`: when set, every Bash call rewrites `last.json` there (the heartbeat the liveness probe reads, task #407),
  and a call whose decision comes after the size floor also writes `<UTC day>/<time>-<tool use id>.json`, one file per
  call so parallel calls never share a file (the runtime's `$.fs` has no append). A record holds the diagnostics object's
  counts (upstream's own `diagnostics` line, now built by one function for both) plus `at`; never the command or the
  output. A failed write is swallowed: a record never changes the tool result. `sourceEstimatedTokens` is computed when
  either `diagnostics` or `decisionsDir` is on.

`tests/test_jev_pruner_floor.py` drives the real hook for each (four `change3` tests; six hook mutants, each killed by
them, 2026-10-01). No `src/` file changed, so `dist/` was not rebuilt.

```diff
--- a/hooks/fast-jev-output.ts
+++ b/hooks/fast-jev-output.ts
@@ -16,6 +16,11 @@ import type { InformationCategory } from '../src/retention.js';
 export { looksSecret } from '../src/secrets.js';
 
 const ARCHIVE_DIR = '.claude/fast-jev-output';
+// agent-factory local change 3 (vendor/jev-pruner/PROVENANCE.md): the decisions taken before the size floor. A call
+// that ends on one of them gets the heartbeat record only; any other decision also gets a record of its own.
+const BEFORE_THE_FLOOR = new Set([
+  'denied', 'tool_error', 'missing_result', 'archive_recovery', 'persisted_disabled', 'below_threshold',
+]);
 const DEFAULT_MAX_SCORING_REQUESTS = 11;
 const VISIBLE_CHARS_PER_REQUEST = 192;
 const DEFAULTS = {
@@ -46,6 +51,10 @@ export type HookFetch = (
 
 export type HookConfig = {
   apiKey?: string;
+  // agent-factory local change 3: the scorer's URL (the owner's patch, ported), the archive folder, the decision records.
+  baseUrl?: string;
+  archiveDir: string;
+  decisionsDir?: string;
   chunkChars?: number;
   diagnostics?: boolean;
   chunkLines: number;
@@ -84,12 +93,17 @@ export function resolveHookConfig(options: PluginOptions): HookConfig {
       typeof options.persistedOutputs === 'boolean' ? options.persistedOutputs : true,
     persistedMaxChars: optionNumber(options, 'persistedMaxChars', DEFAULTS.persistedMaxChars),
     model: optionString(options, 'model') ?? DEFAULTS.model,
+    archiveDir: optionString(options, 'archiveDir') ?? ARCHIVE_DIR,
   };
   const apiKey = optionString(options, 'apiKey');
   if (apiKey) config.apiKey = apiKey;
   const chunkChars = optionNumber(options, 'chunkChars', 0);
   if (chunkChars > 0) config.chunkChars = chunkChars;
   if (options.diagnostics === true) config.diagnostics = true;
+  const baseUrl = optionString(options, 'baseUrl');
+  if (baseUrl) config.baseUrl = baseUrl;
+  const decisionsDir = optionString(options, 'decisionsDir');
+  if (decisionsDir) config.decisionsDir = decisionsDir;
   if (options.maxScoringRequests !== undefined) {
     config.maxScoringRequests = Math.max(0, Math.floor(
       optionNumber(options, 'maxScoringRequests', DEFAULT_MAX_SCORING_REQUESTS),
@@ -98,10 +112,10 @@ export function resolveHookConfig(options: PluginOptions): HookConfig {
   return config;
 }
 
-export function jevAsker(fetchFn: HookFetch, apiKey: string, model: string): JevAsker {
+export function jevAsker(fetchFn: HookFetch, apiKey: string, model: string, baseUrl?: string): JevAsker {
   return {
     async ask(state, questions) {
-      const request = buildJevRequest({ apiKey, model }, state, questions);
+      const request = buildJevRequest({ apiKey, model, baseUrl }, state, questions);
       const response = await fetchFn(request.url, {
         method: request.method,
         headers: request.headers,
@@ -179,7 +193,7 @@ export const register: Register = (on: On, options: PluginOptions) => {
       stage = 'read_output';
       const output = persisted ? await $.fs.read(persisted) : record.stdout;
       sourceChars = output.length;
-      if (configured.diagnostics) sourceEstimatedTokens = estimateTokens(output);
+      if (configured.diagnostics || configured.decisionsDir) sourceEstimatedTokens = estimateTokens(output);
       decision = 'below_threshold';
       if (!exceedsOutputThreshold(output, configured.minTokens, configured.minTokensFloor)) return answer;
       decision = 'binary';
@@ -198,7 +212,7 @@ export const register: Register = (on: On, options: PluginOptions) => {
       const secret = looksSecret(event.command, combined);
       const path = secret
         ? undefined
-        : persisted ?? `${ARCHIVE_DIR}/bash-${event.tool_use_id ?? Date.now()}.txt`;
+        : persisted ?? `${configured.archiveDir}/bash-${event.tool_use_id ?? Date.now()}.txt`;
       const footer = recoveryFooter(path);
       const maxChars = persisted
         ? Math.min(
@@ -217,7 +231,7 @@ export const register: Register = (on: On, options: PluginOptions) => {
       let archived: Promise<void> | undefined;
       const saveOutput = async (): Promise<void> => {
         if (!path || persisted) return;
-        const ignorePath = `${ARCHIVE_DIR}/.gitignore`;
+        const ignorePath = `${configured.archiveDir}/.gitignore`;
         if (!(await $.fs.exists(ignorePath))) await $.fs.write(ignorePath, '*\n');
         await $.fs.write(path, combined);
       };
@@ -241,6 +255,7 @@ export const register: Register = (on: On, options: PluginOptions) => {
           },
           apiKey,
           configured.model,
+          configured.baseUrl,
         ),
         {
           minTokens: configured.minTokens,
@@ -279,26 +294,44 @@ export const register: Register = (on: On, options: PluginOptions) => {
       $.ui.log(`bash output trim skipped (stage=${stage})`);
       return answer;
     } finally {
+      const decisionRecord = () => ({
+        version: 1, toolUseId: event.tool_use_id ?? null, decision, stage,
+        informationCategory,
+        persisted: Boolean(original?.persistedOutputPath),
+        modelVisibleCharsBefore: answer.text?.length ?? null,
+        modelVisibleBudgetChars,
+        sourceChars, sourceEstimatedTokens, hookStdoutCharsBefore, hookStdoutCharsAfter,
+        hookStderrCharsBefore: original?.stderr.length ?? null,
+        hookStderrCharsAfter: decision === 'pruned' && original?.persistedOutputPath
+          ? 0 : original?.stderr.length ?? null,
+        chunks: pruning?.chunks ?? 0, kept: pruning?.kept ?? 0, dropped: pruning?.dropped ?? 0,
+        withinChunkOnly: Boolean(pruning?.trimmed && pruning.dropped === 0),
+        requests, requestLimit, elapsedMs: Date.now() - started,
+      });
       if (configured.diagnostics) {
         try {
-          $.ui.log(`fast-jev-output decision ${JSON.stringify({
-            version: 1, toolUseId: event.tool_use_id ?? null, decision, stage,
-            informationCategory,
-            persisted: Boolean(original?.persistedOutputPath),
-            modelVisibleCharsBefore: answer.text?.length ?? null,
-            modelVisibleBudgetChars,
-            sourceChars, sourceEstimatedTokens, hookStdoutCharsBefore, hookStdoutCharsAfter,
-            hookStderrCharsBefore: original?.stderr.length ?? null,
-            hookStderrCharsAfter: decision === 'pruned' && original?.persistedOutputPath
-              ? 0 : original?.stderr.length ?? null,
-            chunks: pruning?.chunks ?? 0, kept: pruning?.kept ?? 0, dropped: pruning?.dropped ?? 0,
-            withinChunkOnly: Boolean(pruning?.trimmed && pruning.dropped === 0),
-            requests, requestLimit, elapsedMs: Date.now() - started,
-          })}`);
+          $.ui.log(`fast-jev-output decision ${JSON.stringify(decisionRecord())}`);
         } catch {
           // Diagnostics cannot change the tool result.
         }
       }
+      // agent-factory local change 3: the decision record, counts only (never the command or the output). last.json is
+      // the heartbeat every Bash call rewrites; a decision taken past the size floor also gets a file of its own under
+      // the UTC day, one file per call, so parallel calls never write the same file.
+      if (configured.decisionsDir) {
+        try {
+          const at = new Date(started).toISOString();
+          const line = `${JSON.stringify({ at, ...decisionRecord() })}\n`;
+          await $.fs.write(`${configured.decisionsDir}/last.json`, line);
+          if (!BEFORE_THE_FLOOR.has(decision)) {
+            const id = String(event.tool_use_id ?? 'none').replace(/[^A-Za-z0-9_-]/g, '_');
+            const name = `${at.slice(0, 10)}/${at.replace(/[:.]/g, '')}-${id}.json`;
+            await $.fs.write(`${configured.decisionsDir}/${name}`, line);
+          }
+        } catch {
+          // A decision record cannot change the tool result.
+        }
+      }
     }
   });
 };
```

```diff
--- a/.claude-plugin/plugin.json
+++ b/.claude-plugin/plugin.json
@@ -71,6 +71,21 @@
       "description": "Additional Jev calls beyond the first, shared by scoring, retries and refinement. The hook also limits total calls to one per 192 visible preview characters, rounded up. 0 permits only the initial call.",
       "default": 11
     },
+    "baseUrl": {
+      "type": "string",
+      "title": "System One endpoint URL",
+      "description": "Overrides https://api.typesafe.ai/v1/systemone, e.g. a local relay or a local model server. agent-factory local change 3."
+    },
+    "archiveDir": {
+      "type": "string",
+      "title": "Archive folder",
+      "description": "Where a trimmed output's full text is saved for recovery. Default .claude/fast-jev-output. agent-factory local change 3."
+    },
+    "decisionsDir": {
+      "type": "string",
+      "title": "Decision record folder",
+      "description": "If set, every Bash call rewrites last.json here, and a call past the size floor also writes <UTC day>/<time>-<tool use id>.json. Counts only, never the command or the output. agent-factory local change 3."
+    },
     "model": {
       "type": "string",
       "title": "Jev model",
```

### Change 4: the history window and the version (task #436, 2026-10-01)

One number option, unset by default, so without it the behavior is change 3's exactly; and the copy's version, raised
to 0.1.1 in both manifests, because `claude plugin update` installs only a new version (with the version unchanged it
reports `already at the latest version (0.1.0)`).

- `historyTokens`: upstream partitions the WHOLE session's messages into slices that fit the state budget and scores
  every chunk against every slice; a chunk not scored against all of them is kept (`incomplete_coverage`). The hook allows
  12 requests per output, so in a session longer than about 12 slices nothing is ever pruned. Live on 2026-10-01 at
  09:26Z: a 7,588-token output, 11 chunks, 12 requests through the relay, all 11 kept. With the option the hook passes
  `trimOutput` only the newest run of whole messages whose history entries fit `historyTokens` estimated tokens
  (`recentMessages`, measured with the library's own `historyEntries` and `estimateStateTokens`), so a window at or under
  half of `maxStateTokens` is one slice. The task (`goal`, the last three prompts) is still read from the whole session.
  A newest message that alone is over the budget gives an empty window: Jev then scores against the task and the command.
  The option takes a finite number of at least 1 (rounded down); anything else leaves the whole session.
- The decision record gains `sessionMessages` and `historyMessages` (counts only), the live sign that the window runs.

`tests/test_jev_pruner_floor.py` drives the real hook on a 400-message session of more than 100,000 estimated tokens with
a scorer that answers noul 0 for every chunk: without the option, 12 requests and nothing pruned (`incomplete_coverage`);
with `historyTokens` 2000, one request and 13 of 15 chunks dropped, the task still the session's last three prompts. Four
`change4` tests; nine hook mutants, each killed by them (2026-10-01). No `src/` file changed, so `dist/` was not rebuilt.
An update reaches a running Claude Code only at its next start: an option change reloads the hook code already loaded
(measured 2026-10-01: 0.1.1 installed at 09:41Z, an option changed, and the next record still lacked the new fields).

```diff
--- a/hooks/fast-jev-output.ts
+++ b/hooks/fast-jev-output.ts
@@ -5,7 +5,8 @@ import type {
   SessionMessage,
 } from 'claude-code';
 
-import { DEFAULT_MODEL, buildJevRequest, estimateTokens, parseJevResponse } from '../src/jev.js';
+import { DEFAULT_MODEL, buildJevRequest, estimateStateTokens, estimateTokens, parseJevResponse } from '../src/jev.js';
+import { historyEntries } from '../src/history.js';
 import { classifyOutput, exceedsOutputThreshold, looksBinary, MIN_OUTPUT_TOKENS, recoveryFooter, trimOutput } from '../src/output.js';
 import type { TrimOutputResult } from '../src/output.js';
 import type { JevAsker } from '../src/jev.js';
@@ -55,6 +56,8 @@ export type HookConfig = {
   baseUrl?: string;
   archiveDir: string;
   decisionsDir?: string;
+  // agent-factory local change 4: the history Jev scores against is the newest this many estimated tokens of it.
+  historyTokens?: number;
   chunkChars?: number;
   diagnostics?: boolean;
   chunkLines: number;
@@ -104,6 +107,10 @@ export function resolveHookConfig(options: PluginOptions): HookConfig {
   if (baseUrl) config.baseUrl = baseUrl;
   const decisionsDir = optionString(options, 'decisionsDir');
   if (decisionsDir) config.decisionsDir = decisionsDir;
+  // agent-factory local change 4: a finite number of at least 1 sets the window; anything else keeps the upstream's
+  // whole-session history.
+  const historyTokens = Math.floor(optionNumber(options, 'historyTokens', 0));
+  if (historyTokens >= 1) config.historyTokens = historyTokens;
   if (options.maxScoringRequests !== undefined) {
     config.maxScoringRequests = Math.max(0, Math.floor(
       optionNumber(options, 'maxScoringRequests', DEFAULT_MAX_SCORING_REQUESTS),
@@ -139,6 +146,21 @@ export function goalFromMessages(messages: readonly SessionMessage[]): string {
     .join('\n');
 }
 
+/**
+ * agent-factory local change 4 (vendor/jev-pruner/PROVENANCE.md): the newest run of whole messages whose history
+ * entries fit `historyTokens`. Upstream scores every chunk against every slice of the whole session and keeps any chunk
+ * not scored against all of them, so a session with more slices than the request allowance was never pruned (the live
+ * test of 2026-10-01: 12 requests, 11 chunks, all kept as incomplete_coverage). A window that fits the history's share
+ * of `maxStateTokens` (at least half) is one slice. The newest message alone over the budget gives an empty window.
+ */
+export function recentMessages(messages: readonly SessionMessage[], historyTokens: number): SessionMessage[] {
+  let start = messages.length;
+  while (start > 0 && estimateStateTokens(JSON.stringify(historyEntries(messages.slice(start - 1)))) <= historyTokens) {
+    start -= 1;
+  }
+  return messages.slice(start);
+}
+
 /** Key lookup order: plugin option, TYPESAFE_API_KEY, EVAL_TYPESAFE_API_KEY, settings env. */
 export async function getApiKey(
   $: {
@@ -177,6 +199,8 @@ export const register: Register = (on: On, options: PluginOptions) => {
     let sourceEstimatedTokens: number | null = null;
     let modelVisibleBudgetChars: number | null = null;
     let requestLimit: number | null = null;
+    let sessionMessages: number | null = null;
+    let historyMessages: number | null = null;
     let pruning: TrimOutputResult | undefined;
     let informationCategory: InformationCategory | null = null;
     const original = answer.deny === undefined && !answer.isError ? answer.result : undefined;
@@ -209,6 +233,10 @@ export const register: Register = (on: On, options: PluginOptions) => {
       stage = 'history';
       const messages = await $.session.messages();
       const goal = goalFromMessages(messages);
+      // agent-factory local change 4: Jev reads the newest historyTokens of the history; the task stays whole.
+      const history = configured.historyTokens ? recentMessages(messages, configured.historyTokens) : messages;
+      sessionMessages = messages.length;
+      historyMessages = history.length;
       const secret = looksSecret(event.command, combined);
       const path = secret
         ? undefined
@@ -240,7 +268,7 @@ export const register: Register = (on: On, options: PluginOptions) => {
         {
           command: event.command,
           goal,
-          messages,
+          messages: history,
           output,
           fullOutputPath: path,
         },
@@ -307,6 +335,7 @@ export const register: Register = (on: On, options: PluginOptions) => {
         chunks: pruning?.chunks ?? 0, kept: pruning?.kept ?? 0, dropped: pruning?.dropped ?? 0,
         withinChunkOnly: Boolean(pruning?.trimmed && pruning.dropped === 0),
         requests, requestLimit, elapsedMs: Date.now() - started,
+        sessionMessages, historyMessages,  // agent-factory local change 4
       });
       if (configured.diagnostics) {
         try {
```

```diff
--- a/.claude-plugin/plugin.json
+++ b/.claude-plugin/plugin.json
@@ -1,6 +1,6 @@
 {
   "name": "fast-jev-output-floor",
-  "version": "0.1.0",
+  "version": "0.1.1",
   "description": "Trim long Bash output with Jev before the model sees it (Claude Code plugin)",
   "license": "MIT",
   "userConfig": {
@@ -86,6 +86,11 @@
       "title": "Decision record folder",
       "description": "If set, every Bash call rewrites last.json here, and a call past the size floor also writes <UTC day>/<time>-<tool use id>.json. Counts only, never the command or the output. agent-factory local change 3."
     },
+    "historyTokens": {
+      "type": "number",
+      "title": "History window tokens",
+      "description": "If set (1 or more), Jev scores against the newest whole messages that fit this many estimated tokens instead of every slice of the session; the task (the last three prompts) is unchanged. Keep it at or under half of maxStateTokens so the window is one slice. Unset, a long session leaves every chunk unscored and kept. agent-factory local change 4."
+    },
     "model": {
       "type": "string",
       "title": "Jev model",
```

```diff
--- a/.claude-plugin/marketplace.json
+++ b/.claude-plugin/marketplace.json
@@ -9,7 +9,7 @@
       "name": "fast-jev-output-floor",
       "source": "./",
       "description": "Trim long Bash output with Jev before the model sees it (Claude Code plugin)",
-      "version": "0.1.0",
+      "version": "0.1.1",
       "license": "MIT"
     }
   ]
```

## Rebuilding and re-checking

1. `git -C <checkout> archive 47d017c src tsconfig.json package.json | tar -x -C <dir>`, apply the `src/output.ts` diff above,
   and run TypeScript 5.9.3 as above. The result must equal this `dist/` byte for byte.
2. Without the diff, the build must equal the installed plugin's `dist/` byte for byte (the check done at vendoring).
3. The manifests: `git -C <checkout> show 47d017c:.claude-plugin/<file>` plus the diffs above must give the files here byte
   for byte; `tests/test_jev_pruner_floor.py` undoes the diffs and compares the git blob ids.
