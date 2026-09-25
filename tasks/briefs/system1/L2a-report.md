# L2a report: the code-map cache, its builder and its reader (D-090, design L2)

Lane: L2a, code-implementer (sandbox, Opus 5.5). Brief: `tasks/briefs/system1/L2a-brief.md` (PIN c3a00b7; the tree's HEAD
at start was cac6fe6, whose two commits after the pin are the brief itself and a transcripts digest: no file this lane reads
changed). Started 2026-09-25 18:2xZ, finished 20:0xZ. Written incrementally.

## 0. PREMISE — re-measured at start (2026-09-25 18:23Z)

| brief's fact | measured now | verdict |
|---|---|---|
| graft skeleton scripts/jev.py: rc=0 ms=501 bytes=2574 | rc=0 ms=571 bytes=2573 | holds |
| gitnexus impact rank: rc=0 ms=1946, "ambiguous", 5 symbols | rc=0 ms=2245 bytes=2844, "ambiguous", "Found 5 symbols matching 'rank'" | holds |
| crg query tests_for scripts/jev.py: rc=0 ms=298 bytes=417 | rc=0 ms=318 bytes=416; 0 results, and the output says "graph is stale: built at an older commit than HEAD" | holds (the 0 is a finding: see section 9) |
| ap_screen.py scripts/jev.py: rc=0 ms=71 bytes=246 | rc=0 ms=75 bytes=245 (AF-AP-72 at :347, AP-32 at :429) | holds |
| GitNexus CLI has context, impact, cypher | yes; `impact -f/--file` only disambiguates a NAMED target (there is no per-file impact) | holds |
| post-commit launchers at 123, 126, 132, 135 | the same four lines | holds |
| .jev/codemap/x.json is git-ignored | ignored | holds |
| scripts/codemap.py, tests/test_codemap.py absent | absent | holds |
| disk 1.9G free | 1.9G | holds |

No mismatch that matters: the lane proceeds.

## 1. Seams read before writing code (verified against the installed tools, not docs)

| seam | what the code actually does | consequence |
|---|---|---|
| GitNexus 1.6.10 risk | `dist/mcp/local/local-backend.js:6289-6322`: an upstream walk with no callers is `UNKNOWN`; else CRITICAL/HIGH/MEDIUM/LOW from direct count, processes, modules and the depth-3 impacted count | risk comes only from `impact`; a Cypher re-computation would re-implement it (rejected) |
| GitNexus `impact -f` | disambiguates a NAMED target; `impact` on a File node gives one file-level answer | there is no per-file per-symbol impact; batching means one server process for many calls |
| GitNexus MCP (`gitnexus mcp`, stdio) | ready in 0.36 s; each tool result is JSON followed by a `---` hint; a struct column (`RETURN {..} AS row`) returns one JSON object per row | parse with `raw_decode`; one row per struct |
| GitNexus `repo` argument | omitted, the server answers from the ONLY registered repo, which can be another checkout (measured: a copy's query answered from the original) | every call passes `repo` = the root path |
| GitNexus lines | `startLine`/`endLine` are 0-based; graft's spans are 1-based; both exclude decorators (measured on `packet.py`, `ci_gate.py`) | join graft and GitNexus symbols on start+1 |
| freshness stamps | GitNexus `meta.json.fileHashes[path]` (written after the DB swap: `newFileHashesRecord` at `run-analyze.js:2824`, and the #2614 F1 comment); graft `graft/.cache/fingerprint.*.json files[path][2]` (written right after `wiring.json` by `writeFingerprint`, `graph/build.js:276-280`); code-review-graph `nodes.file_hash` of the File node. All three are the sha256 of the file bytes (measured equal to `sha256sum` on `scripts/ap_screen.py`) | the refresh can verify, per file, that each graph indexed exactly the content it packs |
| code-review-graph update | `incremental.py:1455-1520` (`existing_nodes`, then `_run_python_resolver`): stores `file_hash` per parsed file, then runs the Python resolver (TESTED_BY) after | a matching hash alone does not prove crg finished; the refresh also waits until the re-index lock is free |
| code-review-graph `query tests_for <path>` | works on a file path (6 tests for `scripts/ap_screen.py`); `file_summary` of a relative path also matched `sandbox-kit/reference-scripts/push_clean.sh` | pass the absolute path; filter results by exact path |
| graft skeleton | `--json`; without `--no-refresh` a query rebuilds graft's graph under its own `.sync.lock` | the build passes `--no-refresh` (read-only; freshness is checked from the fingerprint instead) |
| ap_screen | `screen_texts` over (name, text) with the rows of `.claude/hooks/edit-snapshot.py` (`AP_SCREEN`, each row id, pattern, message) | the build calls it in-process with the file's text |
| held lock, read without taking it | `/proc/locks` lists each FLOCK as `maj:min:inode` in hex:hex:dec; measured to match `os.stat` of a held lock | the refresh never takes a re-index lock (taking it, even for a moment, would make a starting re-index skip) |

## 2. Contract 2: the batched GitNexus call (measured 2026-09-25 18:4xZ, this tree, one run each)

| file (symbols) | per-symbol CLI `impact --uid --summary-only` | one MCP session, impact per symbol, sequential | one MCP session, pipelined | cypher: the file's symbols | cypher: the file's direct callers | risk equal across forms |
|---|---|---|---|---|---|---|
| scripts/ap_screen.py (5) | 9.02 s (1.80 s/symbol) | 3.14 s | 2.45 s | 0.84 s (includes the DB open) | 0.07 s | yes |
| scripts/ci_gate.py (28) | 49.73 s (1.78 s/symbol) | 14.69 s | 9.85 s (0.35 s/symbol) | 0.79 s | 0.07 s | yes |
| scripts/mojev_probe.py (78, the largest) | not run (extrapolated 139 s) | 38.37 s | 22.80 s (0.29 s/symbol) | 0.79 s | 0.07 s | seq = pipelined |

Choice: one `gitnexus mcp` session per build, one Cypher per file for the symbols and one for their direct callers, and
the `impact` calls for the file's symbols pipelined into that session (5-6x cheaper than the per-symbol CLI, the same
risk values). One Cypher per file cannot give GitNexus's risk without re-implementing its walk and thresholds, so it
gives the callers only. `impact` with a file target answers for the File node (who imports it), not per symbol.

## 3. What was built (the gates are in section 7)

- `scripts/codemap.py` (new): `build [--all] PATH...`, `refresh --commit --lock-dir --graphs --wait --grace -- PATH...`,
  `lookup PATH --line N [--end-line M] [--json]`, `demo PAYLOAD|-`; Python API `lookup(path, line, end_line=None,
  root=None)` and `edit_context(file_path, old_string, root=None, replace_all=False)` for L2b. Packs at
  `.jev/codemap/<path>.json` (git-ignored), written atomically (temp file + `os.replace`).
- `tests/test_codemap.py` (new): a fixture repo indexed by the REAL graft, GitNexus and code-review-graph under an
  isolated HOME, copied per test; 14 checks (9 on the pack and the reader, 5 on the refresh), each failed by one or more of 18
  mutants of `codemap.py` or the hook with its exact message, plus static and unit tests: 41 tests.
- `scripts/hooks/post-commit` (modified, the refresh trigger only): 29 lines inserted after the re-index log line
  (`145a146,174`), nothing else changed. Written in scratch, `bash -n`, run through the existing hook tests
  (`test_post_commit_reindex.py`, `test_hooks_worktree.py`, the hook part of `test_slopo.py`: 44 passed) and through
  this lane's refresh tests with scratch copies pointed at it (14 passed, then the 6 refresh mutants with exact
  messages: 8 passed), then moved into place with one `mv` on the same filesystem (device 65024) at 19:13:09Z;
  sha256 `199841bbdf44d82dbfee9e41bb3b94812be94fbeeac74e3a27662bdccb9fd06d`.

### The pack (one per code file)

`schema, path, language, blob` (git's blob id of the bytes packed, checked equal to `git hash-object`), `sha256, lines,
bytes, commit` (HEAD at build), `symbols_from` (graft, or code-review-graph for a type graft does not parse),
`caller_files`, `instruments` (per instrument: `status` ok / no-data / n/a / absent / no-index / error, a `note`, and for
the three graphs `graph` fresh / stale / not-indexed with the `indexed_sha256` the graph recorded), `symbols` (name,
qualname by containment, kind, start, end, `from` = the first decorator line from the file's own AST, signature, and
`gitnexus`: id, risk, impacted, direct, callers {count, tests, sample of up to 3 name/file/line}), `tests` (crg
`tests_for`: file, line, name, indirect), `registry` (row, line, text, message), `built_at`, `timing` (started, per
instrument ms, total ms).

### The brief's question: a symbol GitNexus answers with risk UNKNOWN

The pack keeps `risk: "UNKNOWN"` and never writes a 0 in its place; the entry says it in words: `risk UNKNOWN —
unresolved, not zero: GitNexus resolved no caller outside tests; a dynamic call, getattr, a callback, an argparse type=
or a module run by path leaves no edge. Confirm with: grep -rnw '<name>' .` When GitNexus's CALLS edges still name
callers (test callers, which `impact` excludes), the line adds their count. A mutant that says "no callers" instead
fails `check_lookup_positions` ("UNKNOWN is not said as unresolved").

### Other languages

| type (in scope) | symbols | callers and risk | tests | registry rows |
|---|---|---|---|---|
| Python `.py` | graft skeleton | GitNexus | code-review-graph | ap_screen |
| JavaScript/TypeScript (`.mjs` etc.; 2 files in scope) | graft | GitNexus (when it indexed the file: `harness-ports/bin/omni_api.mjs` is not in its fileHashes) | code-review-graph | ap_screen (its rows are written for Python) |
| shell `.sh`, `.bash`, and extension-less files with a sh/bash shebang (hooks) | code-review-graph `file_summary` (bash functions) | none: GitNexus does not parse shell (the entry says `GitNexus n/a`) | code-review-graph (a test that runs the script leaves no edge) | ap_screen (AF-AP-145 and AF-AP-175 are shell rows) |
| extension-less Python (`scripts/proof-runner`, `validate-ledger`, `ledger-gen`, `decide-harvest`) | code-review-graph | none (neither graft nor GitNexus reads a file with no extension) | code-review-graph | ap_screen |
| anything else under the prefixes (json, yaml, txt, logs) | no pack: `lookup` says out of scope | | | |

## 4. The measurement table (this tree, 2026-09-25 19:1x-19:4xZ; 4 cores shared with live lanes; one run each unless said)

| what | measured | how |
|---|---|---|
| graft `skeleton --json --no-refresh`, per Python file | median 399 ms, p95 543, max 714 (121 files, 48.8 s in all) | the packs' `timing.graft_ms`, full build |
| code-review-graph `query tests_for` (+ `file_summary` for shell), per file | Python median 290 ms, p95 537; shell (2 queries) median 543, p95 599 | `timing.code_review_graph_ms` |
| GitNexus, per Python file: 2 Cypher + the file's `impact` calls pipelined in one session | median 1,840 ms, p95 13,456, max 26,211 (mojev_probe.py, 78 symbols); 1,382 symbols in 447.2 s = 324 ms/symbol | `timing.gitnexus_ms` |
| GitNexus batched choice (section 2) | per-symbol CLI 1.78-1.80 s/symbol; one session pipelined 0.29-0.35 s/symbol; same risk | 3 files |
| ap_screen in process, per file | median 7 ms (Python), 3 ms (shell), max 76 | `timing.ap_screen_ms` |
| a typical commit's refresh, build part | 5abf6b9 (chat_find.py + its test): 3 packs (widened by 2: hiccup_scan.py, transcript_export.py), 41.5 s; 1dc723e (setup.sh, strip_cbm_hooks.py + test): 2 packs, 4.0 s; 283faf0 (5 paths): 4 packs, 5.8 s build after a 30 s grace (its tests/test_slopo.py is modified in the working tree by another hand, so no graph held its bytes) | `codemap.py refresh` in the tree |
| a typical commit's refresh, wait part | the slowest graph's re-index: at 4ac98e7 (launched 19:20:53) crg ended 19:20:58, graft 19:21:02, GitNexus 19:23:11 (138 s); at 283faf0, GitNexus 85 s | `/tmp/*-build.log` mtimes, `post-commit-reindex.log` |
| the full build `build --all`, niced | 217 files (121 Python incl. 4 extension-less, 94 shell, 2 JS), 217 built, 602.9 s, 1,262,127 pack bytes | `nice -n 19 ionice -c 3`, 19:23:52-19:33:55Z |
| pack sizes | median 2,605 bytes, p95 20,827, max 43,155 | the 217 packs |
| lookup, in process (the hook's path) | p50 0.181 ms, p95 0.406 ms, max 0.875 ms over 1,000 seeded lookups (398 hit, 526 module, 76 past-end); entry text p50 452 bytes, p95 965, max 1,381 | `lookup()` after `import codemap` (16.3 ms once) |
| lookup, CLI | p50 45.9 ms, p95 60.0 ms, max 79.2 ms over the same 1,000 | `python3 scripts/codemap.py lookup` |
| graph states in the 217 packs (after the span cross-check) | graft fresh 107, no-data 11 (fresh), stale 1, n/a 98; GitNexus fresh 105, not-indexed 12, stale 2, n/a 98; crg fresh 216, stale 1 | stale: all three graphs for `scripts/transcript_export.py` (modified in the working tree by SCRUB1), and GitNexus for `proofs/S0-08/check_containment.py` (its record lies, below) |
| risk levels, all symbols | LOW 1,035, UNKNOWN 259, HIGH 49, CRITICAL 32, MEDIUM 24, none 496 (shell functions, not-indexed files) | the packs |

One line: GitNexus impact dominates (324 ms/symbol even batched); a typical commit refreshes in 4-42 s after its
slowest re-index (GitNexus, 85-138 s here); the full build takes 603 s niced for 217 files and 1.26 MB; a lookup takes
0.18 ms (p50) and 0.41 ms (p95) in process.

### Cross-file staleness (contract 4): measured, and widened

Measured over the last 300 non-merge commits (52 changed a Python file under the prefixes or `tests/`):
- calls that RESOLVE through an import of an in-scope module (`from M import f` / `M.f()`), diffed between parent and
  commit: 6 of 52 commits (12%) changed the callers of 1-2 OTHER in-scope files (median 1.5, max 2). A looser name match
  gives 62-65%, an over-count (stdlib names).
- GitNexus's own edges (every in-scope file a changed file calls into, current graph): median 0 files, p90 2, max 3;
  38 of 52 commits add none.
Chosen: widen. After the wait, the refresh adds every in-scope file the changed code and test files call into (one
GitNexus Cypher per changed file, on the graph it waited for) and every file whose pack names a caller in a changed
file (`caller_files`: a call this commit removed), capped at 20. A commit that changes only `tests/*.py` launches a
refresh for its callees. NOT covered: risk counts up to depth 3 in files further away drift until their own file changes
or a full build runs (stated in NOT-done).

### A graph's freshness record can lie (found while measuring)

GitNexus's `meta.json` holds the sha256 of the CURRENT `proofs/S0-08/check_containment.py`, but its 18 nodes for that
file sit 3 lines higher (`Deferred` at 0-based 97 = line 98; the file has it at 101): exactly the lines of the version
before 7f60d83 (09-14). Its incremental analyze updated the hash without re-parsing the file. The per-file stamp alone
would have called that graph fresh. Measured over the packs: 1 of 105 GitNexus-fresh files, 0 of 107 graft files (graft
differs from the AST only on END lines, where it counts trailing comments into a function). The pack now checks each
graph's start lines against the file's own AST (Python) or the pack's symbols: a disagreement marks that graph stale
with a note, and GitNexus data is then joined by unique name and flagged (`matched_by`); the entry says "from a STALE
GitNexus graph, lines may be off". Test: `check_record_that_lies` reproduces it in the fixture; its mutant
`trust-the-record` fails.

### The setup.sh line (proposed, NOT added)

After the graft, code-review-graph and codebase-memory launches in `scripts/setup.sh`:
```
# code map (L2a, D-090): every pack, once this session's graph builds are done; niced, in the background (603 s for
# 217 files on 2026-09-25). A graph that has not indexed a file's bytes is marked stale or not-indexed in that pack.
if [ ! -d "$REPO_ROOT/.jev/codemap" ]; then
  (cd "$REPO_ROOT" && nohup nice -n 19 ionice -c 3 sh -c 'sleep 240; while pgrep -f "[g]raft build|[c]ode-review-graph build|[g]itnexus analyze" >/dev/null; do sleep 15; done; python3 scripts/codemap.py build --all' >/tmp/codemap-build.log 2>&1 &)
fi
```
setup.sh launches no `gitnexus analyze` itself (resume-heal and the post-commit hook do); on a container with no
`.gitnexus/`, the packs name GitNexus `no-index` until the next full build.

## 5. How the refresh ordering is solved

The hook launches the refresh after the re-index launches, in the background, niced, under a BLOCKING flock on
`$T/codemap-refresh.lock` (one refresh at a time; a later commit's refresh queues), and passes it `--graphs
"$launched"` (the graphs the hook re-indexes for THIS commit). `codemap.py refresh` then waits, per graph and per file
that graph parses, until two things hold:
1. the graph's re-index lock (`$T/graft-build.lock`, `$T/gitnexus-analyze.lock`, `$T/crg-build.lock`) is not held,
   read from `/proc/locks` and never taken (taking it, even for an instant, would make a re-index starting at that
   instant skip its `flock -n`; test `test_lock_held_is_read_without_taking_the_lock`);
2. the graph's own record of the file's bytes (the sha256 each graph keeps per file) equals the file's sha256.
The lock alone cannot close the race the brief names: a refresh that looks before the re-index subshell has taken its
lock sees a free lock and an old graph. The record closes it (test `refresh-that-starts-first-waits`, whose mutant
`lock-only-wait` fails). The record alone is not enough either: code-review-graph writes a file's hash before its
Python resolver adds the TESTED_BY edges (`existing_nodes` hash check to `_run_python_resolver`,
`incremental.py:1455-1520`), and a record can lie (section 4), so the lock check stays and the spans are cross-checked. Bounds: while a lock is held the refresh waits up to `--wait` (1,200 s);
when the lock is free but the record is behind, it waits `--grace` (30 s) from the last time the lock was seen held,
which covers a re-index not yet started; after that no re-index is coming (skipped because an older build held the
lock, or failed) and the pack is built with that graph marked stale, never trusted (test `gives-up-and-marks-stale`).

## 6. Tests (tests/test_codemap.py)

The fixture repo holds `scripts/alpha.py` (a function, a class with two methods, a decorated function, a nested
function, a module-level AP-1 line, an AP-32 line inside a function, two `try:` blocks), `scripts/beta.py` and
`scripts/user.py` (callers in other files), `tests/test_alpha.py` (a test caller), `scripts/tool.sh` (a shell
function), `scripts/long.py` (an entry past the byte cap: 3-byte characters in its registry lines). Indexed once by the
real graft, GitNexus and code-review-graph under an isolated HOME; each test copies it (and removes the copy after).

| brief's evidence demand | check (positive) | mutant(s) that must fail it, with the exact failure |
|---|---|---|
| the pack's fields | `pack-fields`: blob = `git hash-object`, sha256, bytes, lines = `wc -l`, commit = HEAD, all four sections ok/fresh, symbols and spans = the file's own AST (decorators included), helper's risk LOW and its 3 callers by file:line (tests counted), main UNKNOWN with count 0, crg's test, registry rows (AP-1 :6, AP-32 :26) with messages, caller_files | `blob-without-header` ("blob is not git's blob id"), `spans-without-decorators` ("the symbols and spans differ from the file's own AST") |
| lookup in a function, a method, module level, past the end | `lookup-positions`: helper, Box.get, main.inner (nested), the decorator line gives `cached`, a blank line between defs and line 6 are module level, line 999 past-end, a range over two methods gives Box, main says UNKNOWN as unresolved | `outermost-symbol` ("a method line did not give the method"), `no-past-end` ("a line past the end: module"), `unknown-read-as-none` ("UNKNOWN is not said as unresolved") |
| the stale flag after an edit | `stale`: False, then True with "STALE" after an append | `never-stale` |
| a miss | `miss`: no pack gives status miss and stale None; a Markdown file is out of scope | `miss-as-module` ("a missing pack is not a miss") |
| the byte cap | `byte-cap`: the long entry is at most 1,500 bytes, ends with the cut marker, decodes; every line of the file stays under the cap; `test_cap_cuts_on_a_character_boundary` (every offset of a 3-byte character) | `no-cap` ("the entry is 1[5-9]xx bytes") |
| an absent instrument named as absent | `absent`: PATH without graft and GitNexus: both `absent` with a note, symbols from code-review-graph, the entry says so | `absent-as-empty` ("an absent graft is not named absent") |
| two builds identical apart from times | `identical`: alpha.py and tool.sh built twice, equal after dropping `built_at` and `timing` | `time-in-a-field` |
| the demo (Edit payload) | `edit-context`: a multi-line old_string whose first line occurs first in another function (D8) lands at 32-33 in `main`; a repeated one is `ambiguous` with both ranges; an absent one a miss; the `demo` CLI prints the range, the symbol, the entry | `first-line-only` ("the edit was not placed at 32-33: ... occurs 2 times") |
| a record that lies (found here) | `record-that-lies`: GitNexus's record set to new bytes its nodes do not reflect: the section is stale with a note, data joined by name | `trust-the-record` |
| a code commit refreshes its files after their re-index | `commit-refresh-after-reindex`: the real hook through `git commit`, each re-index slowed 2 s inside its own lock by a shim; no refresh result exists when the commit returns; one launch line; the pack's `timing.started` is after every re-index's end; all graphs fresh; the new `gamma` has its caller in beta.py | `refresh-without-graphs` (hook: `--graphs ""`; "the pack was built before the re-index ended") |
| the race the brief names | `refresh-that-starts-first-waits`: the refresh starts 1.5 s before the hook's own launch lines take their locks | `no-wait`, `lock-only-wait` (both "the refresh read the graphs before their re-index ended") |
| a graph that never catches up | `gives-up-and-marks-stale` | `stale-read-as-fresh` |
| a docs-only commit refreshes nothing | `docs-only-commit`: README.md, scripts/notes.md, tasks/briefs/probe.py, wiki/a.md: one `none:` line, no `.jev/`, no second line | `docs-plane-not-skipped` (hook; "a docs-only commit launched a refresh") |
| cross-file callers (widening) | `widening`: a call added in beta.py rebuilds alpha.py's pack (GitNexus edges); a call removed from user.py rebuilds it again (the old pack named the caller) | `no-widening` ("an added call did not widen") |

Also: `test_risk_equals_gitnexus_per_symbol_cli` (the batched session's risk and impacted count equal the per-symbol
CLI for 3 symbols); `test_shell_file_gets_crg_symbols_and_says_what_is_not_parsed`;
`test_codemap_reads_and_locks_are_the_hook_s` (READS, LOCKS and the launch line equal the hook's own text) with its
negative control (a renamed lock, a dropped extension); `test_a_hung_gitnexus_costs_one_timeout_per_build_not_one_per_file`
(a fake server that answers `initialize` and then hangs: the first batch times out in 2 s, the next file fails at once
and names it); `test_lock_held_is_read_without_taking_the_lock`; two tests hold every check to at least one mutant.
The fixture, the shims and the fake hung server are the only non-real parts; every pack in every check comes from the
real instruments. Without graft, gitnexus or code-review-graph installed (CI), the instrument tests SKIP with the
reason printed (the sibling pattern of `tests/test_slopo.py`); the static, cap, lock and hang tests run everywhere.

## 7. Gates (pasted)

Set: `tests/test_codemap.py tests/test_hooks_worktree.py tests/test_post_commit_reindex.py tests/test_shell_syntax.py
tests/test_slopo.py` = `5 files set=d798bbae6f87` (the formula of `pc_suite.sh set-id`, computed locally: `printf '%s\n'
<files> | sort | sha256sum | cut -c1-12`). `bash scripts/test_summary.sh --basetemp <scratch> <the 5 files>`, twice:

```
run 1 start 19:47:46Z
pytest-exit: 0
pytest-summary: 108 passed in 333.47s (0:05:33)
run 1 rc 0 end 19:53:20Z
run 2 start 19:53:20Z
pytest-exit: 0
pytest-summary: 108 passed in 337.46s (0:05:37)
run 2 rc 0 end 19:58:57Z
```
0 skipped in both (41 + 6 + 14 + 4 + 43 collected). `tests/test_slopo.py` was modified in the working tree by another
hand at the time (section 11). An earlier start of this gate was stopped by its process group id after 1 minute to fix
two weaknesses (section 10, item 1; the e2e non-blocking assertion); no result from it is used.

- Red then green on the real change: `test_codemap_reads_and_locks_are_the_hook_s` failed on the tree's hook before
  the install (`assert None`: no refresh launch line in it) and passes after. Every other check's red side is its
  mutants (section 6), run in the same gate.
- `python3 -m pyflakes scripts/codemap.py tests/test_codemap.py`: rc 0. `bash -n scripts/hooks/post-commit`: rc 0.
- `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`: 0 for `scripts/codemap.py`, `tests/test_codemap.py`,
  `scripts/hooks/post-commit`, this report.
- `scripts/report_lint.py` on this report (the installed tools' files mapped by alias): `report_lint: 5 refs — OK 5,
  NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.
- `node .gitnexus/run.cjs detect-changes --scope all`: `Changes: 4 files, 33 symbols`, `Risk level: low`, 0 affected
  processes, none of them this lane's (the two new files are untracked; GitNexus parses no extension-less hook).
- `scripts/ap_screen.py` over the whole files: `tests/test_codemap.py` (TEST_SCREEN) 0 hits; `scripts/hooks/post-commit`
  0 hits; `scripts/codemap.py` 8 hits (final file), each classified: AP-32 x2 (:113, :647, the sha256 of file bytes:
  measured equal to all three graphs' records; `pack-fields` asserts it), AF-AP-40 x2 (:636 removing a deleted file's
  pack, :751 no pack directory means no recorded callers: neither is a required artifact), AF-AP-115 (:250
  `shutil.which` on PATH: codemap is advisory, never a gate, and must run the binaries the hook re-indexed with, resolved
  the hook's way), AF-AP-175 (:625 HEAD read once per build, a label; identity is the bytes read), AF-AP-25 (:523 the
  parse of the screen's printout: guarded, a count that differs from the screen's own total is an error, never "no
  rows"), AF-AP-72 (:185 `int(tok, 16)` of `/proc/locks` text, ValueError caught).

## 8. NOT done (stated first-class)

- NOT built: the L2b hook that injects an entry (`.claude/hooks/system1-context.py` belongs to S1-L1-R1; L2b is after
  it). The Python API it will call exists (`lookup`, `edit_context`) and is tested.
- NOT added: the `setup.sh` line (proposed in section 4, as the brief asked).
- NOT run: anything on the PC (no bridge by the brief). `/proc/locks` exists on Linux; the PC (Fedora) venue is NOT
  verified. Where `/proc/locks` is unreadable, `lock_held` returns None, the wait falls back to the records alone and
  the result line says so (then crg's resolver window is not covered).
- NOT tested in a linked worktree (the PC lanes' venue): there the refresh finds no graph index of its own unless the
  lane built one, waits the grace, and names those graphs `no-index` or `not-indexed`; `$T` (`/tmp`) and its locks are
  shared with the main tree, so it may also wait for the main tree's re-index.
- NOT covered by widening: a changed caller changes the depth-2/3 risk of symbols in files further away; those packs
  drift until their own file changes or a full build runs. The entry shows the pack's instruments and states; it does
  not show the pack's age.
- NOT packed: `tests/` (outside the brief's prefixes; a changed test only widens), json/yaml/text files under the
  prefixes, and `.md`. GitNexus has not indexed 12 in-scope files (mostly `harness-ports/bin/*.py` with hyphens, and
  `proofs/*/fixtures/`): their packs say GitNexus `not-indexed`.
- NOT measured: a refresh's wall time on the PC, a full build on a fresh container (the tree's graphs already existed),
  and lookup latency with a cold page cache.
- The registry rows' messages come from `.claude/hooks/edit-snapshot.py`; a row's fix is not in the entry (the
  registry in `docs/INCIDENT-LOG.md` is), only its one-line message (cut at 90 characters in the entry).
- NOT registered: the anti-pattern classes this lane found (section 10) — `docs/INCIDENT-LOG.md` is outside the boundary.

## 9. DISCREPANCIES (flagged)

- The brief says "one log line per commit". The hook writes exactly one line per commit to
  `$T/codemap-refresh.log`; a launched refresh adds its own result line there (the slopo block's pattern), so a code
  commit leaves two lines.
- The brief's scope is five prefixes; the hook also passes changed `tests/*.py` to the refresh, as callers only (they
  get no pack), so a tests-only commit can widen. This is the widening choice (section 4), beyond the letter of the
  brief.
- The brief says "`scripts/codemap.py build <file>...` writes one pack per code file"; `build` on a deleted file
  REMOVES its pack (the refresh passes deleted paths).
- The brief names `impact --file` as a batched form to measure: it does not exist as a per-symbol form in GitNexus
  1.6.10 (`-f` disambiguates a named target; a File target answers for the file node). Measured and reported instead:
  per-symbol CLI, one session sequential, one session pipelined, one Cypher per file.
- The premise's `tests_for scripts/jev.py` returned 0 with "graph is stale": the 0 is also real at a fresh graph for
  files whose tests load them by path or run them as subprocesses (e.g. `scripts/ci_gate.py` has 0 though
  `tests/test_ci_gate.py` exists); the entry says "none found" with that reason, never "untested".
- `scripts/codemap.py` reads three graphs' internal records (GitNexus `meta.json`, graft's fingerprint JSON,
  code-review-graph's sqlite) for freshness. They are not public contracts: a format change reads as "unknown", which
  never counts as fresh (the wait then gives up after the grace and marks the graph stale).

## 10. Self-attack: the three likeliest ways this is wrong

1. **The refresh stalls the queue.** A refresh holds `$T/codemap-refresh.lock` while it waits (up to 1,200 s for a held
   lock). A hung GitNexus server would have cost 300 s per file; fixed: a failed session is dead for the rest of the
   build (`test_a_hung_gitnexus...`: the second call returns in under 1 s). Residual: a re-index that holds its lock
   for more than 20 minutes delays every queued refresh by that long (the queue is serial by design). Measured waits:
   85-138 s.
2. **A pack marked fresh that is not.** Ruled out as far as measured: freshness needs the graph's record to equal the
   file's sha256 AND the graph's start lines to agree with the file's own AST (or the pack's symbols). The one lying
   record in this tree (GitNexus, check_containment.py) is caught; graft agreed with the AST on every start line of
   107 files. Not ruled out: a graph whose nodes are stale in callers or edges but not in spans (the cross-check sees
   only spans).
3. **The ordering tests pass for a reason other than the ordering.** Ruled out by the mutants: without the wait, with
   the lock-only wait, and with the hook passing no graphs, the same checks fail with "built before the re-index
   ended" (the pack's `timing.started` against the shims' recorded end times, not a wall-clock guess), and the race
   test starts the refresh BEFORE the re-index takes its lock. Residual: the fixture's re-index is 2 s plus a 10 s
   analyze; the tree's is 85-138 s; only the bound differs.

Also attacked and ruled out: the GitNexus `repo` argument (omitted, a copy's query answered from the original checkout;
every call now names the repo by path, and the tests run on registered copies); select() on a buffered pipe (the
session reads the raw fd with its own buffer); the widening firing on nothing (median 0 extra files; capped at 20).

## 11. Adjacent defects and observations (reported, not fixed)

- **GitNexus 1.6.10: a fileHashes entry that claims bytes its nodes do not reflect** (upstream bug candidate; a
  registry class for the coordinator: "an instrument's freshness record is one instrument's self-report; cross-check it
  against the bytes"). Evidence: `proofs/S0-08/check_containment.py`, current sha256 `52668a02...` in `meta.json`,
  nodes at the 09-14 lines (`class Deferred`: GitNexus 0-based 97, file line 101; line 98 in `7f60d83^`).
- **graft counts trailing comment lines into a function's span** (`proofs/S0-01/tools/scripted_backend.py`
  `make_handler.Handler._stream`: graft 792-817, AST 792-815). Harmless for lookup (a comment line after a function resolves to it).
- **code-review-graph `query file_summary <path>` also returns another file with the same basename**
  (`scripts/push_clean.sh` also gave `sandbox-kit/reference-scripts/push_clean.sh`), even with an absolute path;
  codemap filters by exact path.
- **The S1 context hook's `push` rows fire on a path inside heredoc text** (18:4xZ: my report append named
  `sandbox-kit/reference-scripts/push_clean.sh`; the row's pattern `push_clean\.sh\b` matched the data, not a command).
  Advisory, never blocking; a false positive for its telemetry.
- `tests/test_slopo.py` became modified in the working tree during this lane by another hand (a CI fix for the wrapper
  tests); the gate below ran on that state.
- `scripts/transcript_export.py` (SCRUB1's, modified in the working tree): all three graphs hold the committed bytes, so
  its pack says stale for all three, correctly.
