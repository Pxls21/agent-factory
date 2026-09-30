# Provenance: vendor/jev-pruner

- **Upstream:** https://github.com/tamaratran/jev-pruner (package `fast-jev-output` 0.1.0)
- **Pin:** commit `47d017c34eab7690b95f075ce6f4839247c5dc0a` (2026-09-19 10:18:30 +0000, "Merge pull request #64")
- **License:** MIT (`LICENSE`, copied verbatim; sha256 `06dcddbb6908a0c6dd4a9e8ec822eea41d5a460a53089fecccc8a68049e99241`)
- **Pinned in:** `upstream.lock.yaml` `advisory_tooling.jev-pruner`; registered as a vendored root in
  `scripts/vendored_manifest.py` (`VENDORED_ROOTS`) and `sandbox-kit/VENDORED-FROM.md`.
- **Vendored:** 2026-09-25 by the P1 build lane (task #231, seed `seeds/seed-jev-pipes-p1-v1.yaml`, D-087).
- **Changed:** 2026-09-30 by the T408 build lane (task #408, D-118 item 2): local change 2 (the floor as a hook option)
  and the plugin manifests, so the copy installs as a plugin of its own (below).
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
| `.claude-plugin/plugin.json` | `db3a0b1ed98aaae664a4c2ac8c5143c9d2c0b3d6` | `f1f83c08607e7b78bcb049213523d076a180269d131a7a24453d0746c9ebb9ca` |
| `.claude-plugin/marketplace.json` | `6b3748fc216ab50a65eccdbbad4197dd2b2a147b` | `486e2105a4a307ef66fcd576ef74775ca3e2497fa7e3b830201aefc565419989` |
| `hooks/hooks.json` (copied 2026-09-25, unchanged) | `b929bab3cdf8e42c2f8b9abcd6ef27a438ab0e52` | `f880049cfcf59ed9f324e6440ac1b924602945141b0925820d968403c767f240` |

The plugin needs no other file to load. `claude plugin validate` (Claude Code 2.1.285, run under `unshare --net` on scratch
copies of the commit) follows the hook's imports: `plugin.json`, `hooks/hooks.json`, `hooks/fast-jev-output.ts` and
`src/{jev,output,history,retention,secrets}.ts` pass; without `src/history.ts` it reports `cannot import "./history.js"`;
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

There are TWO local changes, plus the manifests' own (below). Both lower the output-size floor only when asked.

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

## Rebuilding and re-checking

1. `git -C <checkout> archive 47d017c src tsconfig.json package.json | tar -x -C <dir>`, apply the `src/output.ts` diff above,
   and run TypeScript 5.9.3 as above. The result must equal this `dist/` byte for byte.
2. Without the diff, the build must equal the installed plugin's `dist/` byte for byte (the check done at vendoring).
3. The manifests: `git -C <checkout> show 47d017c:.claude-plugin/<file>` plus the diffs above must give the files here byte
   for byte; `tests/test_jev_pruner_floor.py` undoes the diffs and compares the git blob ids.
