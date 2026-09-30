# T408: the pruner's lower floor, in our own installable copy (task #408, D-118)

Role: sandbox `code-implementer` (Opus 5.5). Do NOT spawn subagents. Return the whole report as your final message.

PIN: origin 2df97aa (CI run #1189 passed); `vendor/jev-pruner/` and the jev-pruner entry of `upstream.lock.yaml` are
unchanged from it to HEAD (the premise block below).

## Why

The owner (D-118 item 2, `docs/08_DECISION_LOG.md`): "there's [a] tool that doesn't really activate until it hits 10K
tokens, that should be lowered." The tool is the output pruner `fast-jev-output` (jev-pruner at upstream commit
47d017c, MIT), installed at user scope from `/root/jev-plugins/jev-pruner`. Its hook clamps `minTokens` at 10,000
(`vendor/jev-pruner/hooks/fast-jev-output.ts:76`), and its README says that option "can raise this threshold but cannot
lower it". Our vendored copy (`vendor/jev-pruner/`, task #231; `vendor/jev-pruner/PROVENANCE.md`) already lowers the
floor for LIBRARY callers (`src/output.ts:86-87`, the `minTokensFloor` option), but not in the hook. The goal behind it
(D-118 item 4): Jev used now, its decisions logged as data to train Laya.

## What to build

1. **MODIFY `vendor/jev-pruner/hooks/fast-jev-output.ts`:** read a `minTokensFloor` plugin option (a finite number, at
   least 0; default `MIN_OUTPUT_TOKENS`, so with no option the behavior is upstream's exactly); clamp `minTokens` to that
   floor instead of `MIN_OUTPUT_TOKENS` (line 76); pass the floor to `exceedsOutputThreshold` (line 178) and in the
   `trimOutput` options (line 240), so the two gates agree.
2. **CREATE `vendor/jev-pruner/.claude-plugin/plugin.json` and `vendor/jev-pruner/hooks/hooks.json`** from the upstream
   commit object (`git -C /root/jev-plugins/jev-pruner show 47d017c34eab7690b95f075ce6f4839247c5dc0a:<path>`), plus one
   `minTokensFloor` entry in the manifest's options schema (title, description, number, default 10000, minimum 0).
   Copy, do not redesign. Any other file the plugin needs in order to load comes from the same commit object and is
   named in PROVENANCE: read the upstream tree and the installed plugin to find out which.
3. **Make the copy installable as a local marketplace**, the way `scripts/setup.sh:109-113` installs honey from
   `sandbox-kit/honey-for-devs/` (read its `.claude-plugin/marketplace.json` and `plugin.json`). CREATE the marketplace
   manifest under `vendor/`. Give the marketplace and the plugin names distinct from the owner's
   `fast-jev-output@fast-jev-output`, so both can be installed side by side; say which names you chose and why.
4. **`dist/`:** rebuild only if a `src/` file changes (it should not). If you rebuild, use the TypeScript version
   PROVENANCE names (5.9.3), not the PATH's (6.0.2), and say how you ran it.
5. **MODIFY `vendor/jev-pruner/PROVENANCE.md`** (the second local change as a diff; the added files with their upstream
   blob ids) and the jev-pruner entry of `upstream.lock.yaml` (its `vendored_at` text only).
6. **CREATE `tests/test_jev_pruner_floor.py`** (pytest, LLM-free, no network). Drive the REAL hook module with node
   (its option resolution and its threshold gate, through the module's own exports or entry): with no option the floor
   is 10,000 (an output estimated over 10,000 tokens passes, one under does not); `minTokensFloor` 500 with `minTokens`
   600 (over 600 passes, between 500 and 600 does not); `minTokens` under the floor (the floor wins); a negative or
   non-finite floor (the fallback you document); the two gates agree for each case. Each case red on the unchanged hook
   first, for its own reason; paste the reds. The plugin manifest validates (`claude plugin validate` if it runs here;
   otherwise a JSON check, and say so). The marketplace manifest names a plugin path that exists.
7. **Gates:** your new test file; `tests/test_jev_pipes_replay.py tests/test_laya_systemone_server.py` (they name the
   vendored dir); `tests/test_vendored_manifest.py -k test_committed_manifest_matches_fresh_generation`, expected to
   fail on the `vendor/` row until the coordinator regenerates the manifest at the landing (say so if it does; never the
   whole manifest test file: it copies about 3.4 GB). Hand the files back; the coordinator regenerates the manifest.

## NOT yours

The coordinator's, after the owner's decision on the classifier refusal of 15:31Z (D-118 item 2's record): installing,
enabling or disabling any plugin; editing any `settings.json`; pointing the plugin at any backend; starting
`scripts/jev_relay.py`, the Laya server or any other server; sending anything to any host. Write the install commands
the coordinator will run in your report; run none of them.

## Boundary

- CREATE or MODIFY only: `vendor/jev-pruner/hooks/fast-jev-output.ts`, `vendor/jev-pruner/hooks/hooks.json`,
  `vendor/jev-pruner/.claude-plugin/plugin.json`, the marketplace manifest under `vendor/` (your path, named in the
  report), any other upstream file item 2 needs (named in PROVENANCE), `vendor/jev-pruner/PROVENANCE.md`,
  `vendor/jev-pruner/dist/` (only under item 4), `tests/test_jev_pruner_floor.py`, and the jev-pruner entry of
  `upstream.lock.yaml`.
- READ only: `/root/jev-plugins/jev-pruner` (through `git show` of the pinned commit; never modify it, never check
  anything out there), the installed plugin under `/root/.claude/plugins/cache/fast-jev-output/` (never modify),
  `scripts/setup.sh`, `sandbox-kit/honey-for-devs/`.

## STANDING RULES

- The shared tree, no worktree; no commit (the coordinator commits through `scripts/safe_commit.sh`); never
  `git add -A`, stash, checkout, restore or amend; no outward action, no PC bridge, no subagent.
- Never read a secret file (`.pc-bridge.env`, any `*.env`, any key file, `/root/.codiv/`); a secret in a test is a fake
  built at run time.
- `--basetemp` as a pytest ARGUMENT outside every work tree (its parent made first); counts pasted from
  `scripts/test_summary.sh` with their set ids (`bash scripts/pc_suite.sh set-id -- <files>`); a long gate in ONE
  foreground call; stamps from `date -u`.
- Never a top-level `cd` (AF-AP-249): use absolute paths or a `( cd … )` subshell. Stop every process you start, by pid.
- This session's codebase-memory daemon (pid 32217) is not yours: never stop it; a real cbm call on a private cache gets
  a private short `CBM_RUNTIME_DIR` (AF-AP-251).
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.

## Report

Files (sha256, lines), the change in words, each test with its red-first proof, the gates pasted, the install commands
(not run), NOT done, DISCREPANCIES, and how your change could still be wrong. Head it "## T408" with "Written
2026-09-30 from <date -u stamp>".

## PREMISE — MEASURED at authoring (2026-09-30 15:3xZ, main tree; PIN origin 2df97aa)

Printed by `bash scripts/premise_block.sh` from the main tree; re-run it there. Expected to differ: nothing.

```
$ git log -2 --format='%h %s' -- vendor/jev-pruner | cut -c1-100
e8c14bf P1 harvest (task #231): the vendored jev-pruner, replayed on this session's Bash results wit
$ ls -a vendor/jev-pruner | tr '\n' ' '; echo
. .. LICENSE PROVENANCE.md README.md dist hooks package.json src tsconfig.json 
$ grep -n 'minTokens' vendor/jev-pruner/hooks/fast-jev-output.ts
26:  minTokens: MIN_OUTPUT_TOKENS,
55:  minTokens: number;
76:    minTokens: Math.max(MIN_OUTPUT_TOKENS, optionNumber(options, 'minTokens', DEFAULTS.minTokens)),
178:      if (!exceedsOutputThreshold(output, configured.minTokens)) return answer;
240:          minTokens: configured.minTokens,
$ grep -n -E 'MIN_OUTPUT_TOKENS = |minTokensFloor' vendor/jev-pruner/src/output.ts
7:export const MIN_OUTPUT_TOKENS = 10_000;
33:  minTokensFloor?: number;
86:export function exceedsOutputThreshold(output: string, minTokens?: number, minTokensFloor?: number): boolean {
87:  const floor = Math.max(0, finite(minTokensFloor, MIN_OUTPUT_TOKENS));
392:  if (!exceedsOutputThreshold(input.output, options.minTokens, options.minTokensFloor)) return untrimmed(input.output, 0, [], 'below_threshold', options.onDecision);
$ git -C /root/jev-plugins/jev-pruner rev-parse HEAD
47d017c34eab7690b95f075ce6f4839247c5dc0a
$ git -C /root/jev-plugins/jev-pruner ls-tree --name-only 47d017c34eab7690b95f075ce6f4839247c5dc0a | tr '\n' ' '; echo
.agents .claude-plugin .codex-plugin .gitignore LICENSE README.md codex demo evals hooks package-lock.json package.json src tests tsconfig.hooks.json tsconfig.json types 
$ git -C /root/jev-plugins/jev-pruner show 47d017c34eab7690b95f075ce6f4839247c5dc0a:.claude-plugin/plugin.json | grep -n -E '"minTokens"|"name"|"version"'
2:  "name": "fast-jev-output",
3:  "version": "0.1.0",
13:    "minTokens": {
$ git -C /root/jev-plugins/jev-pruner show 47d017c34eab7690b95f075ce6f4839247c5dc0a:hooks/hooks.json | tr -s ' \n' ' ' | cut -c1-300; echo
{ "modules": ["./fast-jev-output.ts"] } 

$ ls sandbox-kit/honey-for-devs/.claude-plugin/ | tr '\n' ' '; echo
marketplace.json plugin.json 
$ grep -n -E 'honey.*(marketplace|plugin install)|plugin marketplace add' scripts/setup.sh | head -4 | cut -c1-160
109:  claude plugin marketplace add "$HONEY_SRC" >/dev/null 2>&1 || true   # idempotent: exists -> no-op
111:    ok "honey@greenpt installed from the vendored local marketplace"
113:    warn "honey plugin install failed — vendored skills/agents under .claude/ still load"
$ grep -n -E 'jev-pruner' upstream.lock.yaml | cut -c1-80
148:  jev-pruner:
149:    repository: https://github.com/tamaratran/jev-pruner
152:    vendored_at: "vendor/jev-pruner/ (PROVENANCE.md: copied from the commit 
$ grep -n -E '"vendor/|vendor/' scripts/vendored_manifest.py | head -3 | cut -c1-120
119:        "vendor/jev-pruner/",
820:    # A tree vendored outside the kit snapshot, under `vendor/`, is declared the honey way:
821:    # its own `**Added ...` line names the backticked `vendor/<name>/` root (P1, task #231).
$ grep -l 'vendor/jev-pruner' tests/*.py harness-ports/tests/* 2>/dev/null | tr '\n' ' '; echo
tests/test_jev_pipes_replay.py tests/test_laya_systemone_server.py tests/test_vendored_manifest.py 
$ node --version; tsc --version
v22.22.2
Version 6.0.2
```
