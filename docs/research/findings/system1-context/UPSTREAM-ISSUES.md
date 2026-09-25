# Upstream issue texts (D-091 items 2 and 4; task #289)

The owner files these (the session's GitHub access does not reach third-party repositories: `add_repo` for
DeusData/codebase-memory-mcp was refused by the permission classifier on 2026-09-25). Each text holds only public facts:
versions, timings and a reproduction, no repository content.

## 1. DeusData/codebase-memory-mcp

**Title:** `hook-augment` reads its whole executable on every call, so it always misses its 2,000 ms deadline and adds nothing

**Body:**

Version: codebase-memory-mcp 0.10.8, the prebuilt Linux x86_64 release binary (293,213,352 bytes).

What happens: the Claude Code hooks the installer registers (`cbm-code-discovery-gate`, which runs
`codebase-memory-mcp hook-augment`) never add context. `~/.cache/codebase-memory-mcp/logs/` fills with
`hook-augment: deadline_exceeded ms=2000` (3,361 lines in one week on our machine). Each Read, Grep and Glob still
waits about 2.0 s for the hook.

Why, from one call under strace (`CBM_HOOK_DEADLINE_MS=10000` so that it completes):

- +0.00 s: opens `/proc/<pid>/exe`.
- +0.02 s to +2.79 s: 4,475 `pread64` calls on that descriptor, 293,213,352 bytes in total: the whole executable.
- +2.80 s: connects to the daemon socket (`/tmp/cbm-daemon-0/cbm-<hash>.sock`).
- +2.87 s: exits, with 614 bytes of context on stdout.

About 97% of each call reads the binary; it looks like a full-file hash that names the daemon's socket or version
cohort. The real work takes about 70 ms. Under the default 2,000 ms deadline the call stops before it reaches the
daemon: 2.02 s wall time and 0 bytes out, on every call. The index size is not the cause (a 91 MB index gives the same
2.0 s). The CLI one-shots pay the same start cost (about 2.4 s for a `search_graph`).

Reproduction:

```
echo '{"session_id":"x","transcript_path":"/dev/null","cwd":"<repo>","hook_event_name":"PreToolUse","tool_name":"Grep","tool_input":{"pattern":"<a symbol in the repo>"}}' \
  | CBM_HOOK_DEADLINE_MS=10000 strace -f -ttt -e trace=openat,pread64,connect codebase-memory-mcp hook-augment
```

Suggestion: compute the binary's identity once and cache it (keyed by path, inode, size and mtime), or take it from the
ELF build id or the embedded version string instead of hashing the whole file.

Workaround we use: we removed the hooks and kept the MCP server and the CLI. `CBM_HOOK_DEADLINE_MS=10000` makes the hook
return context in about 2.7 s, which is too slow to run before every tool call.

## 2. rafal-qa/slopo

**Title:** `slopo index` walks every file under source_dir before it applies source_dir_exclude

**Body:**

**slopo 0.6.0** (the PyPI wheel), Python 3.13 on Linux, pathspec 1.1.x.

`scan_directory` (slopo/indexing/scanner.py) iterates `root.rglob("*")` and tests each path against
`source_dir_exclude` only afterwards. A directory the excludes cover completely is still walked, entry by entry.

Numbers: our repository root holds about 18.1 million files under `.lanes/` and 1.7 million under `.suite/` (lane
worktrees and test scratch), all excluded. The first `slopo index` there took **1,389 s** (23 minutes). The index
needs about 116 files, under four directories. On a clone without those two directories (36,044 files) the full
walk takes 0.33-0.35 s and a walk that skips the excluded directories 0.02-0.03 s, with the same result.

Config (excerpt): `source_dir: .`; `source_dir_exclude: ["/*", "/*/", "!/scripts/", "!/src/", "!/proofs/",
"!/harness-ports/", "**/vendor/", "/proofs/S0-01/tools/archive/"]`.

Suggestion: prune while walking (for example `os.walk` top-down, dropping a directory from `dirnames` when the spec
excludes every path below it). With pathspec's file-by-file, last-match-wins semantics a directory can only be
skipped when no later `!` pattern could match below it, so a conservative check is needed; an explicit
`source_dirs` list (several roots) would also solve our case.

Related: the report bytes depend on the walk order. Unit ids follow the scan order, `sort_cluster` orders a
two-unit cluster by id, and a group of same-body-hash units prints its first unit's raw body. Reversing the scan
order changed 15 of 19 cluster files on the same index (member order in 14, the printed body in 1); the clusters
and their ignore-file hashes did not change. If the walk changes, sorting by path would keep reports stable.

We work around it locally by running the CLI with a pruning walk in place of `scan_directory`; the files, their
order and the clusters are identical to slopo's own walk.

(Drafted by SLOPO2, task #285, from its measurements; the workaround is `scripts/slopo_run.py`.)

## 3. GitNexus (candidate, not ready to file)

L2a (task #284) found one file whose GitNexus record says fresh while its symbols are stale: `meta.json` holds the sha256 of
the current `proofs/S0-08/check_containment.py`, but its 18 nodes carry the start lines of the version before a 2026-09-14
commit (3 lines off). An incremental `analyze` updated the hash without re-parsing the file (GitNexus 1.6.10; 1 of 105
files). Before filing: a minimal reproduction (a repository where an incremental analyze of a line-shifting edit leaves
the nodes behind), which this session has not built. `scripts/codemap.py` guards against it meanwhile.
