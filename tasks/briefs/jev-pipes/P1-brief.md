# P1: the jev-pruner replay harness (task #231; seed `seeds/seed-jev-pipes-p1-v1.yaml`; D-087)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/jev-pipes/P1-report.md` (write it
incrementally from the start). Touch only the boundary below; report adjacent defects, never fix them.

## GOAL

Decide, from this session's own records, whether the owner-recommended jev-pruner saves net tokens and calls at our scale. The
pruner (`fast-jev-output`, enabled at user scope, `baseUrl` the local Laya server 127.0.0.1:47411) ranks the chunks of a Bash output
with a Jev, keeps what matters and archives the rest. Its 10,000-token floor skips 98% of our tool-output text, so it fired twice in
19,358 results. The replay runs the pruner's OWN code at a 2k-character floor over the session's recorded tool results, scores
with the real local Laya server, and prints PASS or FAIL against the seed's bar: misses at or under 5% of pruned results AND net
tokens saved above zero. The seed is the full contract (goal, 14 constraints, 7 acceptance criteria, exit conditions); the JEV-FIT
plan (`docs/research/findings/jev-fit/PLAN-2026-09-25.md`, pipeline P1) is the design context.

## DESIGN (settled; copy, do not redesign)

1. **Vendor the pruner** at `vendor/jev-pruner/` from `/root/jev-plugins/jev-pruner` at commit
   47d017c34eab7690b95f075ce6f4839247c5dc0a (upstream `https://github.com/tamaratran/jev-pruner`, MIT): `src/`, `dist/`, `hooks/`,
   `package.json`, `LICENSE`, `README.md`. No `node_modules` (it has no runtime dependencies). Add `vendor/jev-pruner/PROVENANCE.md`
   (origin, commit, license, every local change as a diff) and an `upstream.lock.yaml` entry under the section that pins
   advisory tooling (read the file's existing shape first; `grep -q 47d017c upstream.lock.yaml` must pass, AC3). A new vendored
   root must be registered the way `sandbox-kit/VENDORED-MANIFEST.md` requires (read `scripts/vendored_manifest.py`).
2. **The one local change:** `trimOutput` (`src/output.ts:669`, `dist/output.js:513`) floors `minTokens` at `MIN_OUTPUT_TOKENS =
   10_000` through `exceedsOutputThreshold` (`src/output.ts:81-83`). Allow a lower floor only when the caller passes an explicit
   option (your name), default unchanged, in BOTH `src` and `dist`. Record it in PROVENANCE. Everything else in the pruner runs as
   shipped: chunking, keep rules (first and last chunk, diagnostics, test totals, paths, unscored chunks), rendering, archive footer.
3. **The replay**, `scripts/jev_pipes/replay_pruner.py` (package `scripts/jev_pipes/`), with a small Node bridge that imports the
   vendored `dist/index.js` and calls `trimOutput(input, asker, options)`; the asker sends the pruner's own request to the local
   Laya server (`/v1/systemone`), under the venue budget (2 s per tool result in the sandbox; record the real latency).
   - Sources: every main-session transcript under `/root/.claude/projects/*/` (this session wrote under two folders, AF-AP-204).
   - Candidates: Bash results of 2,000 characters or more (the pruner's domain; primary verdict). Read and Grep results of 2,000 or
     more go through the same path as a SECONDARY table, not the verdict.
   - The pruner's `history` input is rebuilt from the transcript prefix up to each result, the way the plugin builds it (read its
     `src/history.ts`), so the Jev sees what it would have seen live.
   - One decision row per result to `.jev/pipes/p1-decisions.jsonl` (mode 0600, never committed): transcript path and byte offset
     of the result (the pointer), chunks kept and dropped, characters saved, latency, fail-open reason if any, and the API requests
     that followed until the next compaction.
   - **Tokens saved** = dropped characters / 4.06 (audit A's fitted characters per token) x the requests that followed until the next
     compaction. **A miss** = a dropped chunk whose distinctive tokens (paths, numbers of 3+ digits, identifiers of 6+ characters,
     hex of 7+) appear in the session's next 20 tool inputs or assistant texts and nowhere in the kept text or the earlier history;
     or a re-run of the same command within 20 calls. **A miss costs** one request's whole context (read from the usage record of
     the next request). **Net** = saved minus miss costs.
   - One command prints PASS or FAIL: `python3 scripts/jev_pipes/replay_pruner.py --min-chars 2000 --out <dir>` (AC1).
   - Throughput: the Laya server runs on 2 CPU threads. First run a deterministic stratified sample of at least 300 results (by
     size band); run the full set in the background only if the measured throughput finishes it within 4 hours. The report names
     which it ran.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. Tests `tests/test_jev_pipes_replay.py`, deterministic and LLM-free, run twice with identical counts:
   - recorded scorer answers captured from the real local server into `tests/fixtures/jev_pipes/` (never answers typed from the
     code's own assumptions, AF-AP-42);
   - the accounting (saved, misses, net, verdict) on a small transcript fixture that uses the production record shapes;
   - fail-open for EVERY trip condition, through the vendored pruner via the bridge, against a local misbehaving server in a temp
     port: refused connection, the budget passed, a non-200, an unparseable answer, an answer that does not cover every chunk, and a
     queue deeper than one pending request. Each returns the original text unchanged and records its reason (AC5; `-k failopen` must
     select them);
   - the floor option: default behavior unchanged (a 9,999-token output still passes untouched without the option).
3. The replay run and the committed report `docs/research/findings/jev-pipes/P1-replay-2026-09-25.md`: counts, keep rate, miss
   rate, tokens saved, miss costs, net, latency (p50, p90, fail-open count by reason), the PASS or FAIL verdict, the secondary
   Read/Grep table, and NOT-run. A FAIL is a valid result; the seed's exit conditions name it.
4. Gates: `pyflakes` rc 0; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` prints 0 on every file you wrote; the seed's verify commands
   (AC1, AC2, AC3, AC5, AC6) pasted with their output.
5. The report never quotes session text: counts, rates and pointers only. The decision log stays under `.jev/` (gitignored).

## BOUNDARY

CREATE: `vendor/jev-pruner/` (the copy plus PROVENANCE.md), `scripts/jev_pipes/` (the package and the bridge),
`tests/test_jev_pipes_replay.py`, `tests/fixtures/jev_pipes/`, `docs/research/findings/jev-pipes/P1-replay-2026-09-25.md`, your
report. MODIFY: `upstream.lock.yaml` (one entry), `sandbox-kit/VENDORED-MANIFEST.md` and whatever the vendored-root registration
requires (name each file in the report). READ: everything else. Never touch `/root/jev-plugins/` or the installed plugin, the
running Laya server (never restart it), `scripts/transcript_export.py` or the SESSION-EXPORT lane's files.

## STANDING RULES

No network beyond the loopback Laya server; no PC bridge; no outward-facing action; no git writes (the coordinator commits). Never
print a secret; never search transcripts for keys, tokens or passwords; FAKE strings for anything secret-shaped in fixtures. Long
commands in ONE foreground call, or run in the background and poll with short calls. A pytest `--basetemp` parent must exist first.
The sandbox disk has about 2 GB free; keep your scratch under 500 MB at
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/p1/`.

## PREMISE — MEASURED at authoring (2026-09-25 05:1xZ, the sandbox)

```
$ git -C /root/jev-plugins/jev-pruner rev-parse HEAD; git -C /root/jev-plugins/jev-pruner remote -v | head -1
47d017c34eab7690b95f075ce6f4839247c5dc0a
origin	https://github.com/tamaratran/jev-pruner (fetch)
$ python3 -c "import json;print(json.load(open('/root/jev-plugins/jev-pruner/package.json')).get('dependencies'))"
None
$ du -sh /root/jev-plugins/jev-pruner/{src,dist,hooks,node_modules}
84K src   232K dist   20K hooks   65M node_modules
$ grep -n 'export' /root/jev-plugins/jev-pruner/dist/index.js; grep -n 'MIN_OUTPUT_TOKENS\|export async function trimOutput' /root/jev-plugins/jev-pruner/src/output.ts
dist/index.js:1:export * from './jev.js';
dist/index.js:2:export { trimOutput } from './output.js';
src/output.ts:7:export const MIN_OUTPUT_TOKENS = 10_000;
src/output.ts:82:  return estimateTokens(output) > Math.max(MIN_OUTPUT_TOKENS, finite(minTokens, MIN_OUTPUT_TOKENS));
src/output.ts:669:export async function trimOutput(
$ node --version
v22.22.2
$ curl -s -m 3 -o /dev/null -w '%{http_code}' http://127.0.0.1:47411/health
200
$ git check-ignore -v .jev/pipes/p1-decisions.jsonl
.gitignore:64:.jev/	.jev/pipes/p1-decisions.jsonl
$ (the coordinator's streaming count over the main session transcript, 04:5xZ)
tool results 19,358; 28,546,514 characters; results of 2,000 characters or more: 3,688 (all tools); pruned by the plugin: 2
$ (the seed's verify commands at authoring)
AC1 RED (no scripts/jev_pipes/replay_pruner.py)   AC2 RED (no tests/test_jev_pipes_replay.py)   AC3 RED (no 47d017c in upstream.lock.yaml)
AC5 RED (no tests)   AC6 PASS (IGNORED)   AC4, AC7 artifacts pending
```

Questions for you, not facts: how many of the 3,688 are Bash results (the primary set)? Does the plugin's `history.ts` read the
transcript file itself, or take records from the hook payload?
